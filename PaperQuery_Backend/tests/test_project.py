from types import SimpleNamespace

import pytest

pytest.importorskip('jwt')
pytest.importorskip('langchain_chroma')

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.backend.db.database import Base
from core.backend.db.models import Document
from core.backend.router.dependencies import get_db
from core.backend.router.router_project import router
from core.backend.utils.utils import get_current_user


def test_project_document_scope_and_archive(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'project.db'}", connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        db.add_all([
            Document(uid='paper-a', knowledgeID='lib-a', lid='workspace-a',
                     documentName='A', documentPath='/a.pdf', documentStatus=1),
            Document(uid='paper-b', knowledgeID='lib-b', lid='workspace-b',
                     documentName='B', documentPath='/b.pdf', documentStatus=1),
        ])
        db.commit()

    user = SimpleNamespace(username='alice', workspace_lid='workspace-a')
    app = FastAPI()
    app.include_router(router)

    def db_override():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[get_current_user] = lambda: user
    client = TestClient(app)
    created = client.post('/projects', json={'name': 'Sample'}).json()['data']
    project_id = created['project_id']
    assert client.post(f'/projects/{project_id}/documents', json={
        'knowledge_id': 'lib-b', 'document_id': 'paper-b'}).status_code == 404
    assert client.post(f'/projects/{project_id}/documents', json={
        'knowledge_id': 'lib-a', 'document_id': 'paper-a'}).status_code == 200
    assert len(client.get(f'/projects/{project_id}/documents').json()['data']) == 1
    user.workspace_lid = 'workspace-b'
    assert client.get(f'/projects/{project_id}/documents').status_code == 404
    user.workspace_lid = 'workspace-a'
    assert client.delete(f'/projects/{project_id}').status_code == 200
    assert client.get('/projects').json()['data'] == []
    assert client.post(f'/projects/{project_id}/restore').status_code == 200
    assert len(client.get('/projects').json()['data']) == 1
