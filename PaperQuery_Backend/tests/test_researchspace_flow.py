import json
from types import SimpleNamespace

import pytest

pytest.importorskip('jwt')

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.backend.db.database import Base
from core.backend.db.models import Artifact, Document, ProjectDocument, ResearchTask, User
from core.backend.router.dependencies import get_db
from core.backend.router import (router_collaboration, router_compare, router_evidence_board,
                                 router_graph, router_project, router_studio, router_timeline)
from core.backend.utils.utils import get_current_user
from core.common.types import EvidenceChunk


class FakeLLM:
    def invoke(self, prompt):
        if '抽取研究方法' in prompt:
            value = {'method_name': 'Method A', 'description': '', 'key_innovations': [],
                     'algorithm': '', 'assumptions': []}
        elif '抽取实验配置' in prompt:
            value = {'datasets': ['Dataset X'], 'metrics': ['MAE'], 'baselines': [],
                     'hyperparameters': {}, 'hardware': ''}
        elif '研究结论或主张' in prompt:
            doc_id = 'paper-a' if 'paper-a:1' in prompt else 'paper-b'
            value = {'claims': [{'quote': 'Method A uses Dataset X and MAE.',
                                 'chunk_id': f'{doc_id}:1'}]}
        else:
            value = {'columns': ['方法'], 'rows': [
                {'document_id': doc_id, 'cells': {'方法': {'value': 'Method A', 'chunk_id': f'{doc_id}:1'}}}
                for doc_id in ('paper-a', 'paper-b')]}
        return SimpleNamespace(content=json.dumps(value))


class FakeProvider:
    def get_llm(self, model):
        return FakeLLM()


class FakeChroma:
    def get_document_chunks(self, doc_id):
        return [EvidenceChunk(chunk_id=f'{doc_id}:1', document_id=doc_id,
            knowledge_id='lib', source='', page_number=2,
            text='Method A uses Dataset X and MAE.')]

    def search_evidence(self, query, filter, k=12):
        return self.get_document_chunks(filter['documentID'])


def test_project_modules_and_source_links(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'flow.db'}", connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        db.add_all([
            User(username='alice', password='x', lid='workspace'),
            User(username='bob', password='x', lid='workspace'),
            Document(uid='paper-a', knowledgeID='lib', lid='workspace',
                     documentName='Paper A', documentPath='/a.pdf', documentStatus=1),
            Document(uid='paper-b', knowledgeID='lib', lid='workspace',
                     documentName='Paper B', documentPath='/b.pdf', documentStatus=1),
        ])
        db.commit()
    app = FastAPI()
    for module in (router_project, router_timeline, router_compare, router_evidence_board,
                   router_graph, router_studio, router_collaboration):
        app.include_router(module.router)
    app.chroma_db = FakeChroma()
    app.llm = FakeProvider()

    def db_override():
        with factory() as db:
            yield db

    user = SimpleNamespace(username='alice', workspace_lid='workspace')
    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[get_current_user] = lambda: user
    client = TestClient(app)
    project_id = client.post('/projects', json={'name': 'Research'}).json()['data']['project_id']
    for doc_id in ('paper-a', 'paper-b'):
        assert client.post(f'/projects/{project_id}/documents', json={
            'knowledge_id': 'lib', 'document_id': doc_id}).status_code == 200
    comparison = client.post(f'/projects/{project_id}/compare', json={
        'question': 'Compare methods', 'document_ids': ['paper-a', 'paper-b'],
        'columns': ['方法']})
    assert comparison.status_code == 200, comparison.text
    assert comparison.json()['data']['rows'][0]['cells']['方法']['citation']['page'] == 2
    claim_id = client.post(f'/projects/{project_id}/evidence', json={
        'title': 'Method claim', 'content': 'Method A is used'}).json()['data']['claim_id']
    citation = client.post(f'/projects/{project_id}/evidence/{claim_id}/citations', json={
        'knowledge_id': 'lib', 'document_id': 'paper-a', 'page_number': 2,
        'chunk_id': 'paper-a:1', 'stance': 'SUPPORT'})
    assert citation.status_code == 200, citation.text
    assert citation.json()['data']['evidence'][0]['source_status'] == 'available'
    studio = client.post(f'/projects/{project_id}/studio', json={'title': 'Draft'}).json()['data']
    assert client.put(f"/projects/{project_id}/studio/{studio['studio_id']}", json={
        'content_markdown': '# Research'}).json()['data']['content_markdown'] == '# Research'
    with factory() as db:
        db.add(ResearchTask(task_id='task-1', lid='workspace', project_id=project_id,
                            goal='Research', status='SUCCESS'))
        db.add(Artifact(artifact_id='artifact-1', task_id='task-1', project_id=project_id,
                        type='research_report', title='Report',
                        data_json=json.dumps({'markdown': '# Report'})))
        db.commit()
    imported = client.post(f'/projects/{project_id}/studio/import-artifact', json={
        'artifact_id': 'artifact-1'})
    assert imported.status_code == 200
    assert imported.json()['data']['content_markdown'] == '# Report'
    assert client.post(f'/projects/{project_id}/collaboration/members', json={
        'username': 'bob', 'role': 'EDITOR'}).status_code == 200
    assert client.post(f'/projects/{project_id}/collaboration/assignments', json={
        'task_id': 'task-1', 'username': 'bob'}).status_code == 200
    assert client.post(f'/projects/{project_id}/collaboration/comments', json={
        'target_type': 'claim', 'target_id': claim_id, 'content': 'Check this'}).status_code == 200
    build = client.post(f'/projects/{project_id}/graph/build')
    assert build.status_code == 200, build.text
    graph = client.get(f'/projects/{project_id}/graph').json()['data']
    assert graph['run']['status'] == 'SUCCESS', graph['run']
    assert {'Paper', 'Method', 'Dataset', 'Metric', 'Claim'}.issubset({node['type'] for node in graph['nodes']})
    timeline = client.get(f'/projects/{project_id}/timeline').json()['data']
    assert {item['event_type'] for item in timeline}.issuperset({
        'PROJECT_CREATED', 'PAPER_ADDED', 'COMPARISON_CREATED', 'CLAIM_CREATED',
        'EVIDENCE_ADDED', 'STUDIO_UPDATED', 'COMMENT_CREATED', 'GRAPH_BUILT'})
    with factory() as db:
        db.query(ProjectDocument).filter_by(project_id=project_id, document_id='paper-a').delete()
        db.query(Document).filter_by(lid='workspace', uid='paper-a').delete()
        db.commit()
    saved_claim = client.get(f'/projects/{project_id}/evidence').json()['data'][0]
    assert saved_claim['evidence'][0]['source_status'] == 'deleted'
    saved_comparison = client.get(f'/projects/{project_id}/compare').json()['data'][0]
    removed = next(row for row in saved_comparison['rows'] if row['document_id'] == 'paper-a')
    assert removed['cells']['方法']['source_status'] == 'deleted'
