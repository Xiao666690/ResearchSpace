"""Research projects and references to workspace papers."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.backend.db.models import (ActivityEvent, Artifact, Document, ProjectDocument,
                                    ResearchProject, ResearchTask)
from core.backend.router.dependencies import get_db
from core.backend.schema.projectschema import ProjectCreate, ProjectDocumentAdd, ProjectUpdate
from core.backend.services.project_service import get_project_or_404, project_documents, require_project_owner
from core.backend.utils.utils import get_current_user

router = APIRouter(prefix='/projects', tags=['projects'])


def _project(row):
    return {'project_id': row.project_id, 'name': row.name,
            'description': row.description or '', 'research_goal': row.research_goal or '',
            'status': row.status, 'created_by': row.created_by,
            'created_at': row.created_at.isoformat() if row.created_at else None}


def _paper(link, document):
    return {'knowledge_id': link.knowledge_id, 'document_id': link.document_id,
            'document_name': document.documentName, 'document_status': document.documentStatus,
            'added_by': link.added_by}


@router.post('')
def create_project(payload: ProjectCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = ResearchProject(project_id=uuid.uuid4().hex, lid=user.workspace_lid,
                          name=payload.name.strip(), description=payload.description,
                          research_goal=payload.research_goal, status='active', created_by=user.username)
    if not row.name:
        raise HTTPException(422, '项目名称不能为空')
    db.add(row)
    db.commit()
    db.refresh(row)
    return {'status_code': 200, 'data': _project(row)}


@router.get('')
def list_projects(include_archived: bool = False, user=Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(ResearchProject).filter(ResearchProject.lid == user.workspace_lid)
    if not include_archived:
        query = query.filter(ResearchProject.status == 'active')
    return {'status_code': 200, 'data': [_project(row) for row in query.order_by(ResearchProject.created_at.desc()).all()]}


@router.get('/{project_id}')
def get_project(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {'status_code': 200, 'data': _project(get_project_or_404(db, project_id, user, include_archived=True))}


@router.put('/{project_id}')
def update_project(project_id: str, payload: ProjectUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = get_project_or_404(db, project_id, user)
    changes = payload.model_dump(exclude_unset=True)
    if 'name' in changes:
        changes['name'] = changes['name'].strip()
        if not changes['name']:
            raise HTTPException(422, '项目名称不能为空')
    for key, value in changes.items():
        setattr(row, key, value)
    db.commit()
    return {'status_code': 200, 'data': _project(row)}


@router.delete('/{project_id}')
def archive_project(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = get_project_or_404(db, project_id, user)
    require_project_owner(row, user)
    row.status = 'archived'
    db.commit()
    return {'status_code': 200, 'data': _project(row)}


@router.post('/{project_id}/restore')
def restore_project(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = get_project_or_404(db, project_id, user, include_archived=True)
    require_project_owner(row, user)
    row.status = 'active'
    db.commit()
    return {'status_code': 200, 'data': _project(row)}


@router.get('/{project_id}/overview')
def overview(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    return {'status_code': 200, 'data': {
        'project': _project(project), 'document_count': len(project_documents(db, project)),
        'task_count': db.query(func.count(ResearchTask.id)).filter_by(project_id=project_id, lid=project.lid).scalar(),
        'artifact_count': db.query(func.count(Artifact.id)).filter_by(project_id=project_id).scalar(),
        'event_count': db.query(func.count(ActivityEvent.id)).filter_by(project_id=project_id, lid=project.lid).scalar(),
    }}


@router.get('/{project_id}/documents')
def list_documents(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    return {'status_code': 200, 'data': [_paper(link, doc) for link, doc in project_documents(db, project)]}


@router.post('/{project_id}/documents')
def add_document(project_id: str, payload: ProjectDocumentAdd, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    doc = db.query(Document).filter_by(lid=project.lid, knowledgeID=payload.knowledge_id,
                                       uid=payload.document_id).first()
    if doc is None:
        raise HTTPException(404, '论文不在当前工作空间中')
    link = db.query(ProjectDocument).filter_by(project_id=project_id,
        knowledge_id=payload.knowledge_id, document_id=payload.document_id).first()
    if link is None:
        link = ProjectDocument(project_id=project_id, knowledge_id=payload.knowledge_id,
                               document_id=payload.document_id, added_by=user.username)
        db.add(link)
        db.commit()
    return {'status_code': 200, 'data': _paper(link, doc)}


@router.delete('/{project_id}/documents/{document_id}')
def remove_document(project_id: str, document_id: str, knowledge_id: str,
                    user=Depends(get_current_user), db: Session = Depends(get_db)):
    get_project_or_404(db, project_id, user)
    link = db.query(ProjectDocument).filter_by(project_id=project_id,
        knowledge_id=knowledge_id, document_id=document_id).first()
    if link is None:
        raise HTTPException(404, '项目论文不存在')
    db.delete(link)
    db.commit()
    return {'status_code': 200, 'msg': '已从项目移除论文'}
