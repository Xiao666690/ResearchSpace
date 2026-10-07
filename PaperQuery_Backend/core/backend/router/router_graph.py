import uuid
from sqlalchemy.orm import sessionmaker

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.backend.db.models import (Document, GraphBuildRun, ResearchEntity, ResearchRelation)
from core.backend.router.dependencies import get_db
from core.backend.services.graph_service import build_graph
from core.backend.services.project_service import get_project_or_404, project_documents
from core.backend.utils.utils import get_current_user

router = APIRouter(prefix='/projects/{project_id}/graph', tags=['graph'])


def _run(row):
    return {'run_id': row.run_id, 'status': row.status, 'error': row.error,
            'created_at': row.created_at.isoformat() if row.created_at else None}


@router.post('/build')
def start_build(project_id: str, background_tasks: BackgroundTasks, request: Request,
                user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    links = project_documents(db, project)
    if not links:
        raise HTTPException(422, '请先向项目添加论文')
    chroma = getattr(request.app, 'chroma_db', None)
    provider = getattr(request.app, 'llm', None)
    if chroma is None or provider is None:
        raise HTTPException(503, '图谱所需的模型或索引未就绪')
    for link, doc in links:
        if doc.documentStatus != 1 or not any(chunk.knowledge_id == link.knowledge_id
                                               for chunk in chroma.get_document_chunks(doc.uid)):
            raise HTTPException(422, f'论文 {doc.documentName} 尚未完成索引')
    current = db.query(GraphBuildRun).filter(GraphBuildRun.project_id == project_id,
        GraphBuildRun.status.in_(['PENDING', 'RUNNING'])).first()
    if current:
        raise HTTPException(409, '已有图谱构建任务正在运行')
    run = GraphBuildRun(run_id=uuid.uuid4().hex, project_id=project_id,
                        status='PENDING', created_by=user.username)
    db.add(run)
    db.commit()
    background_tasks.add_task(build_graph, run.run_id, project_id, chroma, provider,
                              sessionmaker(bind=db.get_bind()))
    return {'status_code': 200, 'data': _run(run)}


@router.get('')
def get_graph(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    entities = db.query(ResearchEntity).filter_by(project_id=project_id).all()
    relations = db.query(ResearchRelation).filter_by(project_id=project_id).all()
    latest = db.query(GraphBuildRun).filter_by(project_id=project_id).order_by(GraphBuildRun.id.desc()).first()
    document_keys = {(doc.knowledgeID, doc.uid) for doc in db.query(Document).filter_by(lid=project.lid).all()}
    return {'status_code': 200, 'data': {
        'run': _run(latest) if latest else None,
        'nodes': [{'id': item.entity_id, 'type': item.entity_type, 'name': item.name,
                   'confidence': item.confidence,
                   'citation': {'knowledge_id': item.knowledge_id, 'document_id': item.document_id,
                                'page': item.page_number, 'chunk_id': item.chunk_id},
                   'source_status': 'available' if (item.knowledge_id, item.document_id) in document_keys else 'deleted'}
                  for item in entities],
        'edges': [{'id': item.relation_id, 'source': item.source_entity_id,
                   'target': item.target_entity_id, 'type': item.relation_type,
                   'confidence': item.confidence,
                   'citation': {'knowledge_id': item.knowledge_id, 'document_id': item.document_id,
                                'page': item.page_number, 'chunk_id': item.chunk_id},
                   'source_status': 'available' if (item.knowledge_id, item.document_id) in document_keys else 'deleted'}
                  for item in relations],
    }}
