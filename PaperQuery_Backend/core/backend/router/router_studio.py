"""Editable project output documents and verified source references."""

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.backend.db.models import Artifact, Document, StudioCitation, StudioDocument
from core.backend.router.dependencies import get_db
from core.backend.services.event_service import emit_event
from core.backend.services.project_service import document_in_project, get_project_or_404
from core.backend.utils.utils import get_current_user

router = APIRouter(prefix='/projects/{project_id}/studio', tags=['studio'])


class StudioCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content_markdown: str = ''


class StudioUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content_markdown: str | None = None


class ArtifactImport(BaseModel):
    artifact_id: str


class CitationCreate(BaseModel):
    citation_key: str = Field(pattern=r'^C[1-9][0-9]*$')
    knowledge_id: str
    document_id: str
    page_number: int = Field(ge=1)
    chunk_id: str


def _serialize(db, row, lid):
    references = db.query(StudioCitation).filter_by(studio_id=row.studio_id).all()
    keys = {(item.knowledge_id, item.source_document_id) for item in references}
    existing = {(doc.knowledgeID, doc.uid) for doc in db.query(Document).filter(
        Document.lid == lid, Document.uid.in_([key[1] for key in keys]) if keys else False).all()}
    return {'studio_id': row.studio_id, 'title': row.title, 'document_type': row.document_type,
            'content_markdown': row.content_markdown, 'created_by': row.created_by,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None,
            'citations': [{'citation_key': item.citation_key, 'knowledge_id': item.knowledge_id,
                           'document_id': item.source_document_id, 'page': item.page_number,
                           'chunk_id': item.chunk_id,
                           'source_status': 'available' if (item.knowledge_id, item.source_document_id) in existing else 'deleted'}
                          for item in references]}


@router.get('')
def list_documents(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    rows = db.query(StudioDocument).filter_by(project_id=project_id).order_by(StudioDocument.id.desc()).all()
    return {'status_code': 200, 'data': [_serialize(db, row, project.lid) for row in rows]}


@router.post('')
def create_document(project_id: str, payload: StudioCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    row = StudioDocument(studio_id=uuid.uuid4().hex, project_id=project_id,
                         title=payload.title.strip(), document_type='note',
                         content_markdown=payload.content_markdown, created_by=user.username)
    if not row.title:
        raise HTTPException(422, '标题不能为空')
    db.add(row)
    emit_event(db, lid=project.lid, project_id=project_id, event_type='STUDIO_UPDATED',
               target_type='studio', target_id=row.studio_id, title=row.title)
    db.commit()
    db.refresh(row)
    return {'status_code': 200, 'data': _serialize(db, row, project.lid)}


@router.get('/{studio_id}')
def get_document(project_id: str, studio_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    row = db.query(StudioDocument).filter_by(project_id=project_id, studio_id=studio_id).first()
    if row is None:
        raise HTTPException(404, '成果文稿不存在')
    return {'status_code': 200, 'data': _serialize(db, row, project.lid)}


@router.put('/{studio_id}')
def update_document(project_id: str, studio_id: str, payload: StudioUpdate,
                    user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    row = db.query(StudioDocument).filter_by(project_id=project_id, studio_id=studio_id).first()
    if row is None:
        raise HTTPException(404, '成果文稿不存在')
    if payload.title is not None:
        row.title = payload.title.strip()
        if not row.title:
            raise HTTPException(422, '标题不能为空')
    if payload.content_markdown is not None:
        row.content_markdown = payload.content_markdown
    emit_event(db, lid=project.lid, project_id=project_id, event_type='STUDIO_UPDATED',
               target_type='studio', target_id=studio_id, title=row.title)
    db.commit()
    return {'status_code': 200, 'data': _serialize(db, row, project.lid)}


def _artifact_markdown(artifact):
    data = json.loads(artifact.data_json or '{}')
    if artifact.type == 'research_report':
        return str(data.get('markdown') or data.get('report') or '')
    if artifact.type == 'paper_list':
        return '\n'.join(f"- {item.get('title', '未命名论文')}" for item in data.get('papers', []))
    if artifact.type == 'comparison_table':
        parsed = data if 'columns' in data else json.loads(data.get('raw') or '{}')
        columns = parsed.get('columns', [])
        lines = ['| 论文 | ' + ' | '.join(columns) + ' |', '| --- | ' + ' | '.join('---' for _ in columns) + ' |']
        for row in parsed.get('rows', []):
            cells = row.get('cells', row)
            values = [str(cells.get(col, {}).get('value', '未验证') if isinstance(cells.get(col), dict)
                          else cells.get(col, '未验证')).replace('|', '\\|') for col in columns]
            lines.append('| ' + str(row.get('paper') or row.get('document_id') or '论文') + ' | ' + ' | '.join(values) + ' |')
        return '\n'.join(lines)
    return '```json\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n```'


@router.post('/import-artifact')
def import_artifact(project_id: str, payload: ArtifactImport, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    artifact = db.query(Artifact).filter_by(artifact_id=payload.artifact_id, project_id=project_id).first()
    if artifact is None:
        raise HTTPException(404, '项目成果不存在')
    try:
        markdown = _artifact_markdown(artifact)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(422, '成果格式无法导入')
    row = StudioDocument(studio_id=uuid.uuid4().hex, project_id=project_id,
        title=(artifact.title or '研究成果')[:255], document_type=artifact.type or 'artifact',
        content_markdown=markdown, created_by=user.username)
    db.add(row)
    emit_event(db, lid=project.lid, project_id=project_id, event_type='STUDIO_UPDATED',
               target_type='studio', target_id=row.studio_id, title=row.title)
    db.commit()
    db.refresh(row)
    return {'status_code': 200, 'data': _serialize(db, row, project.lid)}


@router.post('/{studio_id}/citations')
def add_citation(project_id: str, studio_id: str, payload: CitationCreate, request: Request,
                 user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    row = db.query(StudioDocument).filter_by(project_id=project_id, studio_id=studio_id).first()
    if row is None:
        raise HTTPException(404, '成果文稿不存在')
    if not document_in_project(db, project, payload.knowledge_id, payload.document_id):
        raise HTTPException(403, '引用论文不属于当前项目')
    chroma = getattr(request.app, 'chroma_db', None)
    if chroma is None or not any(chunk.chunk_id == payload.chunk_id and
        chunk.page_number == payload.page_number and chunk.knowledge_id == payload.knowledge_id
        for chunk in chroma.get_document_chunks(payload.document_id)):
        raise HTTPException(422, '无法核对原文引用')
    if db.query(StudioCitation).filter_by(studio_id=studio_id, citation_key=payload.citation_key).first():
        raise HTTPException(409, '引用编号已存在')
    db.add(StudioCitation(studio_id=studio_id, citation_key=payload.citation_key,
        source_document_id=payload.document_id, knowledge_id=payload.knowledge_id,
        page_number=payload.page_number, chunk_id=payload.chunk_id))
    db.commit()
    return {'status_code': 200, 'data': _serialize(db, row, project.lid)}
