from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.backend.db.database import Base
from core.backend.db.models import Document, ProjectDocument, ResearchProject
from core.backend.services.project_service import (get_project_or_404, project_document_ids,
                                                   resolve_project_document_ids, require_parent_project)


def test_project_scope_and_document_reference(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'scope.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        db.add(ResearchProject(project_id='p1', lid='workspace-a', name='Project',
                               created_by='alice', status='active'))
        db.add_all([
            Document(uid='paper', knowledgeID='lib-a', lid='workspace-a', documentName='Paper', documentPath='/paper.pdf'),
            Document(uid='other', knowledgeID='lib-b', lid='workspace-b', documentName='Other', documentPath='/other.pdf'),
            ProjectDocument(project_id='p1', knowledge_id='lib-a', document_id='paper'),
            ProjectDocument(project_id='p1', knowledge_id='lib-b', document_id='other'),
        ])
        db.commit()
        project = get_project_or_404(db, 'p1', SimpleNamespace(workspace_lid='workspace-a'))
        assert project_document_ids(db, project) == {'paper'}
        assert resolve_project_document_ids(db, project, []) == ['paper']
        assert resolve_project_document_ids(db, project, ['paper', 'paper']) == ['paper']
        with pytest.raises(HTTPException) as forbidden:
            resolve_project_document_ids(db, project, ['other'])
        assert forbidden.value.status_code == 403
        with pytest.raises(HTTPException) as wrong_parent:
            require_parent_project(SimpleNamespace(project_id='another-project'), 'p1')
        assert wrong_parent.value.status_code == 403
        with pytest.raises(HTTPException) as exc:
            get_project_or_404(db, 'p1', SimpleNamespace(workspace_lid='workspace-b'))
        assert exc.value.status_code == 404
