"""Project comparison tables with verifiable per-cell citations."""

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.backend.db.models import ComparisonCell, ComparisonSession
from core.backend.router.dependencies import get_db
from core.backend.services.event_service import emit_event
from core.backend.services.project_service import get_project_or_404, project_documents
from core.backend.utils.utils import get_current_user
from core.skills.builtin import PaperCompareInput, PaperCompareSkill

router = APIRouter(prefix='/projects/{project_id}/compare', tags=['compare'])


class CompareCreate(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_ids: list[str] = Field(min_length=2)
    columns: list[str] = Field(default_factory=lambda: ['方法', '数据集', '指标', '局限'])


def _source_for_cell(doc_id, item, chunks):
    """Recover an omitted ID only when the generated value occurs verbatim in source."""
    direct = chunks.get((doc_id, item.get('chunk_id')))
    if direct is not None:
        return direct
    value = str(item.get('value') or '').strip()
    if len(value) < 8 or value == '未验证':
        return None
    matches = [chunk for (source_doc, _), chunk in chunks.items()
               if source_doc == doc_id and value.casefold() in chunk.text.casefold()]
    return min(matches, key=lambda chunk: chunk.page_number) if matches else None


def _serialize(db, session, project):
    cells = db.query(ComparisonCell).filter_by(session_id=session.session_id).all()
    docs = {doc.uid: doc for _, doc in project_documents(db, project)}
    rows = {}
    for cell in cells:
        source_doc = docs.get(cell.evidence_document_id) if cell.evidence_document_id else None
        rows.setdefault(cell.document_id, {})[cell.column_name] = {
            'value': cell.value or '未验证', 'verified': cell.confidence == 'verified' and source_doc is not None,
            'citation': ({'document_id': cell.evidence_document_id, 'knowledge_id': cell.knowledge_id,
                          'page': cell.page_number, 'chunk_id': cell.chunk_id} if source_doc and cell.chunk_id else None),
            'source_status': 'available' if source_doc else ('deleted' if cell.chunk_id else 'unverified'),
        }
    return {'session_id': session.session_id, 'title': session.title, 'question': session.question,
            'columns': json.loads(session.columns_json),
            'rows': [{'document_id': doc_id, 'paper': docs[doc_id].documentName if doc_id in docs else '来源已删除',
                      'cells': values} for doc_id, values in rows.items()],
            'created_at': session.created_at.isoformat() if session.created_at else None}


@router.post('')
async def create_comparison(project_id: str, payload: CompareCreate, request: Request,
                            user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    ids = list(dict.fromkeys(payload.document_ids))
    if len(ids) < 2 or len(ids) > 8:
        raise HTTPException(422, '请选择 2 至 8 篇论文')
    columns = list(dict.fromkeys(value.strip() for value in payload.columns if value.strip()))
    if not columns or len(columns) > 8:
        raise HTTPException(422, '比较列需为 1 至 8 项')
    linked = project_documents(db, project, document_ids=ids)
    docs = {doc.uid: doc for _, doc in linked}
    source_keys = {(link.knowledge_id, link.document_id) for link, _ in linked}
    if set(ids) != set(docs):
        raise HTTPException(403, '比较论文必须属于当前项目')
    chroma = getattr(request.app, 'chroma_db', None)
    provider = getattr(request.app, 'llm', None)
    if chroma is None or provider is None:
        raise HTTPException(503, '比较所需的模型或索引未就绪')
    chunks = {}
    context = []
    for doc_id in ids:
        selected = chroma.search_evidence(payload.question + ' ' + ' '.join(columns),
                                          {'documentID': doc_id}, k=12)
        if not selected:
            raise HTTPException(422, f'论文 {docs[doc_id].documentName} 尚未完成索引')
        context.append(f'论文 document_id={doc_id} 标题={docs[doc_id].documentName}')
        for chunk in selected:
            chunks[(doc_id, chunk.chunk_id)] = chunk
            context.append(f'chunk_id={chunk.chunk_id} page={chunk.page_number}: {chunk.text[:1200]}')
    skill = PaperCompareSkill()
    result = await skill.execute(PaperCompareInput(question=payload.question,
        columns=columns, context='\n'.join(context)), {'llm': provider.get_llm('deepseek')})
    if not result.ok:
        raise HTTPException(502, result.error_message or '比较生成失败')
    generated = result.output['comparison']
    generated_rows = {row.get('document_id'): row.get('cells', {}) for row in generated['rows']
                      if isinstance(row, dict) and row.get('document_id') in docs}
    session = ComparisonSession(session_id=uuid.uuid4().hex, project_id=project_id,
        title=payload.question[:255], question=payload.question, columns_json=json.dumps(columns, ensure_ascii=False),
        created_by=user.username)
    db.add(session)
    for doc_id in ids:
        for column in columns:
            item = generated_rows.get(doc_id, {}).get(column, {})
            if not isinstance(item, dict):
                item = {'value': str(item)}
            chunk = _source_for_cell(doc_id, item, chunks)
            verified = chunk is not None and (chunk.knowledge_id, doc_id) in source_keys
            db.add(ComparisonCell(session_id=session.session_id, document_id=doc_id, column_name=column,
                value=str(item.get('value') or '未验证') if verified else '未验证',
                evidence_document_id=doc_id if verified else None,
                knowledge_id=chunk.knowledge_id if verified else None,
                page_number=chunk.page_number if verified else None,
                chunk_id=chunk.chunk_id if verified else None,
                confidence='verified' if verified else 'unverified'))
    emit_event(db, lid=project.lid, project_id=project_id, event_type='COMPARISON_CREATED',
               target_type='comparison', target_id=session.session_id, title=session.title)
    db.commit()
    db.refresh(session)
    return {'status_code': 200, 'data': _serialize(db, session, project)}


@router.get('')
def list_comparisons(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    sessions = db.query(ComparisonSession).filter_by(project_id=project_id).order_by(ComparisonSession.id.desc()).all()
    return {'status_code': 200, 'data': [_serialize(db, item, project) for item in sessions]}


@router.get('/{session_id}')
def get_comparison(project_id: str, session_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    session = db.query(ComparisonSession).filter_by(project_id=project_id, session_id=session_id).first()
    if not session:
        raise HTTPException(404, '比较不存在')
    return {'status_code': 200, 'data': _serialize(db, session, project)}
