"""Build a project graph from source-matched extracted entities."""

import asyncio
import logging
import uuid

from core.backend.db.models import (Document, GraphBuildRun, ProjectDocument, ResearchEntity,
                                    ResearchProject, ResearchRelation)
from core.backend.services.event_service import emit_event
from core.skills.extract import ExperimentExtractSkill, ExtractInput, MethodExtractSkill
from core.skills.graph_extract import GraphClaimExtractSkill, GraphClaimInput

logger = logging.getLogger(__name__)


def build_graph(run_id, project_id, chroma, llm_provider, db_factory):
    try:
        with db_factory() as db:
            run = db.query(GraphBuildRun).filter_by(run_id=run_id).one()
            run.status = 'RUNNING'
            db.commit()
            project = db.query(ResearchProject).filter_by(project_id=project_id).one()
            links = db.query(ProjectDocument).filter_by(project_id=project_id).all()
            titles = {(doc.knowledgeID, doc.uid): doc.documentName for doc in db.query(Document).filter_by(lid=project.lid).all()}
            lid = project.lid
        llm = llm_provider.get_llm('deepseek')
        entities = []
        relations = []
        seen_papers = set()

        def add_entity(kind, name, chunk, document_id, knowledge_id):
            name = str(name).strip()[:255]
            if not name:
                return None
            row = ResearchEntity(entity_id=uuid.uuid4().hex, project_id=project_id,
                entity_type=kind, name=name, normalized_name=name.casefold(),
                knowledge_id=knowledge_id, document_id=document_id,
                page_number=chunk.page_number, chunk_id=chunk.chunk_id,
                confidence='source_matched')
            entities.append(row)
            return row

        def add_relation(source, target, kind, chunk, document_id, knowledge_id):
            if source and target:
                relations.append(ResearchRelation(relation_id=uuid.uuid4().hex,
                    project_id=project_id, source_entity_id=source.entity_id,
                    target_entity_id=target.entity_id, relation_type=kind,
                    knowledge_id=knowledge_id, document_id=document_id,
                    page_number=chunk.page_number, chunk_id=chunk.chunk_id,
                    confidence='source_matched'))

        for link in links:
            if link.document_id in seen_papers:
                continue
            seen_papers.add(link.document_id)
            chunks = [chunk for chunk in chroma.get_document_chunks(link.document_id)
                      if chunk.knowledge_id == link.knowledge_id]
            if not chunks:
                raise ValueError(f'论文 {link.document_id} 尚未完成索引')
            selected = chroma.search_evidence('research method dataset evaluation metric conclusion',
                {'documentID': link.document_id}, k=16)
            selected = [chunk for chunk in selected if chunk.knowledge_id == link.knowledge_id] or chunks[:12]
            selected = selected[:16]
            by_id = {chunk.chunk_id: chunk for chunk in selected}
            context = '\n\n'.join(f'chunk_id={chunk.chunk_id}, page={chunk.page_number}\n{chunk.text[:1400]}'
                                  for chunk in selected)
            paper = add_entity('Paper', titles.get((link.knowledge_id, link.document_id), link.document_id),
                               chunks[0], link.document_id, link.knowledge_id)
            method = asyncio.run(MethodExtractSkill().execute(ExtractInput(context=context,
                document_id=link.document_id), {'llm': llm}))
            experiment = asyncio.run(ExperimentExtractSkill().execute(ExtractInput(context=context,
                document_id=link.document_id), {'llm': llm}))
            claims = asyncio.run(GraphClaimExtractSkill().execute(GraphClaimInput(context=context), {'llm': llm}))
            if not method.ok or not experiment.ok or not claims.ok:
                raise ValueError('模型抽取失败，图谱未更新')

            def matching_chunk(name):
                return next((chunk for chunk in selected if name.casefold() in chunk.text.casefold()), None)

            method_name = str(method.output.get('method', {}).get('method_name') or '').strip()
            method_chunk = matching_chunk(method_name) if method_name else None
            method_entity = add_entity('Method', method_name, method_chunk, link.document_id, link.knowledge_id) if method_chunk else None
            if method_entity:
                add_relation(paper, method_entity, 'HAS_METHOD', method_chunk, link.document_id, link.knowledge_id)
            experiment_data = experiment.output.get('experiment_config', {})
            for kind, values, relation in [('Dataset', experiment_data.get('datasets', []), 'USES'),
                                           ('Metric', experiment_data.get('metrics', []), 'EVALUATED_BY')]:
                for value in values[:12] if isinstance(values, list) else []:
                    if not isinstance(value, str):
                        continue
                    chunk = matching_chunk(value)
                    if chunk:
                        entity = add_entity(kind, value, chunk, link.document_id, link.knowledge_id)
                        add_relation(method_entity or paper, entity, relation, chunk, link.document_id, link.knowledge_id)
            for claim in claims.output.get('claims', []):
                if not isinstance(claim, dict):
                    continue
                quote = str(claim.get('quote') or '').strip()
                chunk = by_id.get(claim.get('chunk_id'))
                if quote and chunk and quote.casefold() in chunk.text.casefold():
                    entity = add_entity('Claim', quote, chunk, link.document_id, link.knowledge_id)
                    add_relation(paper, entity, 'STATES', chunk, link.document_id, link.knowledge_id)

        with db_factory() as db:
            db.query(ResearchRelation).filter_by(project_id=project_id).delete(synchronize_session=False)
            db.query(ResearchEntity).filter_by(project_id=project_id).delete(synchronize_session=False)
            db.add_all(entities + relations)
            run = db.query(GraphBuildRun).filter_by(run_id=run_id).one()
            run.status = 'SUCCESS'
            emit_event(db, lid=lid, project_id=project_id, event_type='GRAPH_BUILT',
                       target_type='graph', target_id=run_id, title='研究图谱已更新')
            db.commit()
    except Exception as exc:
        logger.exception('Graph build %s failed', run_id)
        with db_factory() as db:
            run = db.query(GraphBuildRun).filter_by(run_id=run_id).first()
            if run:
                run.status = 'FAILED'
                run.error = str(exc)[:1200]
                db.commit()
