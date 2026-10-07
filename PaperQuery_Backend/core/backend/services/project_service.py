"""Workspace-scoped project access and document membership."""

from fastapi import HTTPException

from core.backend.db.models import Document, ProjectDocument, ResearchProject


def get_project_or_404(db, project_id, user, *, include_archived=False):
    project = db.query(ResearchProject).filter(
        ResearchProject.project_id == project_id,
        ResearchProject.lid == user.workspace_lid,
    ).first()
    if project is None or (project.status == 'archived' and not include_archived):
        raise HTTPException(404, '研究项目不存在')
    return project


def require_project_owner(project, user):
    if project.created_by != user.username:
        raise HTTPException(403, '仅项目负责人可管理此项目')


def project_documents(db, project, *, document_ids=None):
    query = db.query(ProjectDocument, Document).join(
        Document,
        (Document.uid == ProjectDocument.document_id) &
        (Document.knowledgeID == ProjectDocument.knowledge_id) &
        (Document.lid == project.lid),
    ).filter(ProjectDocument.project_id == project.project_id)
    if document_ids is not None:
        query = query.filter(ProjectDocument.document_id.in_(document_ids))
    return query.all()


def project_document_ids(db, project):
    return {document.uid for _, document in project_documents(db, project)}


def document_in_project(db, project, knowledge_id, document_id):
    return db.query(ProjectDocument).join(
        Document,
        (Document.uid == ProjectDocument.document_id) &
        (Document.knowledgeID == ProjectDocument.knowledge_id) &
        (Document.lid == project.lid),
    ).filter(ProjectDocument.project_id == project.project_id,
             ProjectDocument.knowledge_id == knowledge_id,
             ProjectDocument.document_id == document_id).first()
