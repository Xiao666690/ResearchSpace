"""Persisted claims and citations from indexed project papers."""

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.backend.db.models import ClaimEvidence, Document, ResearchClaim
from core.backend.router.dependencies import get_db
from core.backend.services.event_service import emit_event
from core.backend.services.project_service import document_in_project, get_project_or_404
from core.backend.utils.utils import get_current_user

router = APIRouter(prefix='/projects/{project_id}/evidence', tags=['evidence'])


class ClaimCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class EvidenceCreate(BaseModel):
    knowledge_id: str
    document_id: str
    page_number: int = Field(ge=1)
    chunk_id: str
    stance: Literal['SUPPORT', 'CONTRADICT', 'CONTEXT', 'INSUFFICIENT'] = 'SUPPORT'


def _claim(db, claim, lid):
    evidence = db.query(ClaimEvidence).filter_by(claim_id=claim.claim_id).all()
    source_keys = {(e.knowledge_id, e.document_id) for e in evidence}
    available = {(doc.knowledgeID, doc.uid) for doc in db.query(Document).filter(
        Document.lid == lid,
        Document.uid.in_([item[1] for item in source_keys]) if source_keys else False).all()}
    return {'claim_id': claim.claim_id, 'title': claim.title, 'content': claim.content,
            'status': claim.status, 'created_by': claim.created_by,
            'created_at': claim.created_at.isoformat() if claim.created_at else None,
            'evidence': [{'evidence_id': row.evidence_id, 'knowledge_id': row.knowledge_id,
                          'document_id': row.document_id, 'page_number': row.page_number,
                          'chunk_id': row.chunk_id, 'text': row.evidence_text,
                          'stance': row.stance, 'confidence': row.confidence,
                          'source_status': 'available' if (row.knowledge_id, row.document_id) in available else 'deleted'}
                         for row in evidence]}


@router.get('')
def list_claims(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    rows = db.query(ResearchClaim).filter_by(project_id=project_id).order_by(ResearchClaim.id.desc()).all()
    return {'status_code': 200, 'data': [_claim(db, item, project.lid) for item in rows]}


@router.post('')
def create_claim(project_id: str, payload: ClaimCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    row = ResearchClaim(claim_id=uuid.uuid4().hex, project_id=project_id,
                        title=payload.title.strip(), content=payload.content.strip(),
                        status='draft', created_by=user.username)
    if not row.title or not row.content:
        raise HTTPException(422, '观点不能为空')
    db.add(row)
    emit_event(db, lid=project.lid, project_id=project_id, event_type='CLAIM_CREATED',
               target_type='claim', target_id=row.claim_id, title=row.title)
    db.commit()
    db.refresh(row)
    return {'status_code': 200, 'data': _claim(db, row, project.lid)}


@router.post('/{claim_id}/citations')
def add_citation(project_id: str, claim_id: str, payload: EvidenceCreate, request: Request,
                 user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    claim = db.query(ResearchClaim).filter_by(project_id=project_id, claim_id=claim_id).first()
    if claim is None:
        raise HTTPException(404, '观点不存在')
    if not document_in_project(db, project, payload.knowledge_id, payload.document_id):
        raise HTTPException(403, '证据论文不属于当前项目')
    chroma = getattr(request.app, 'chroma_db', None)
    if chroma is None:
        raise HTTPException(503, '论文索引未就绪')
    chunk = next((item for item in chroma.get_document_chunks(payload.document_id)
                  if item.chunk_id == payload.chunk_id and item.page_number == payload.page_number
                  and item.knowledge_id == payload.knowledge_id), None)
    if chunk is None:
        raise HTTPException(422, '无法核对原文证据')
    row = ClaimEvidence(evidence_id=uuid.uuid4().hex, claim_id=claim_id,
        knowledge_id=payload.knowledge_id, document_id=payload.document_id,
        page_number=payload.page_number, chunk_id=payload.chunk_id,
        evidence_text=chunk.text[:2000], stance=payload.stance, confidence='verified')
    db.add(row)
    emit_event(db, lid=project.lid, project_id=project_id, event_type='EVIDENCE_ADDED',
               target_type='claim', target_id=claim_id, title=claim.title,
               metadata={'document_id': payload.document_id, 'page': payload.page_number})
    db.commit()
    return {'status_code': 200, 'data': _claim(db, claim, project.lid)}


@router.delete('/{claim_id}')
def delete_claim(project_id: str, claim_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    get_project_or_404(db, project_id, user)
    claim = db.query(ResearchClaim).filter_by(project_id=project_id, claim_id=claim_id).first()
    if claim is None:
        raise HTTPException(404, '观点不存在')
    db.query(ClaimEvidence).filter_by(claim_id=claim_id).delete(synchronize_session=False)
    db.delete(claim)
    db.commit()
    return {'status_code': 200, 'msg': '观点已删除'}
