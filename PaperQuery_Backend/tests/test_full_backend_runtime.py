from types import SimpleNamespace
import fitz
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.backend.db.database import Base
from core.backend.db.models import User, Document
from core.backend.router.dependencies import get_db
from core.backend.router.router_document import validate_pdf_upload
from core.backend.services.translate import Translator
from core.agent.dataprocessAgent import DataProcessAgent
from core.retrieval.sparse import BM25Retriever
from core.retrieval.onnx_hybrid import OnnxHybridRetriever
from core.common.types import EvidenceChunk

class FakeLLM:
    def invoke(self, messages):
        return SimpleNamespace(content='Translated content')
    def stream(self, messages):
        yield SimpleNamespace(content='A test response')

class TestProvider:
    def get_llm(self, name): return FakeLLM()
    def get_stream_llm(self, name): return FakeLLM()
    def get_all_llms(self): return {'deepseek': FakeLLM()}
    def chat_with_llm(self, prompt): return SimpleNamespace(content='invalid JSON')

@pytest.mark.parametrize('source,target', [('en','zh'),('zh','en')])
def test_translation_does_not_require_tencent_or_argos(monkeypatch, source, target):
    monkeypatch.setenv('TRANSLATION_PROVIDER','deepseek')
    assert Translator(source,target,llm=FakeLLM()).translate('Some scientific text') == 'Translated content'

def test_empty_pdf_rejected_before_queueing():
    pdf=fitz.open(); pdf.new_page(); data=pdf.tobytes(); pdf.close()
    with pytest.raises(HTTPException) as err: validate_pdf_upload(data)
    assert err.value.status_code == 422

def test_sparse_ignores_no_token_chunks():
    chunk=EvidenceChunk(chunk_id='x',document_id='x',source='',page_number=1,text='!!!')
    assert BM25Retriever([chunk]).search('science') == []

def test_full_startup_without_key_preserves_data_routes(monkeypatch, tmp_path):
    import main
    monkeypatch.setenv('DEEPSEEK_API_KEY','')
    monkeypatch.setenv('CHROMA_LAYER1_DIR',str(tmp_path/'l1'))
    monkeypatch.setenv('CHROMA_LAYER2_DIR',str(tmp_path/'l2'))
    monkeypatch.setattr(main,'_init_role_and_default_team',lambda: None)
    with TestClient(main.app) as client:
        assert client.get('/health/live').status_code == 200
        assert client.get('/health/ready').status_code == 503
        assert client.get('/user/me').status_code == 401
        cors={'Origin':'http://127.0.0.1:8080'}
        response=client.post('/qa/stream',json={'question':'Hi'},headers=cors)
        assert response.status_code == 503
        assert response.headers['access-control-allow-origin'] == cors['Origin']
        assert client.options('/qa/stream',headers={**cors,'Access-Control-Request-Method':'POST'}).status_code == 200

def test_real_pdf_upload_worker_index_and_source_ids(monkeypatch,tmp_path):
    import main
    from vector import process_next_document
    from core.backend.router.router_user import _hash_password
    monkeypatch.setenv('DEEPSEEK_API_KEY','local-test-only')
    monkeypatch.setenv('CHROMA_LAYER1_DIR',str(tmp_path/'l1'))
    monkeypatch.setenv('CHROMA_LAYER2_DIR',str(tmp_path/'l2'))
    monkeypatch.setenv('PAPER_SAVE_DIR',str(tmp_path/'pdf'))
    monkeypatch.setattr(main,'LLM',TestProvider)
    monkeypatch.setattr(main,'_init_role_and_default_team',lambda: None)
    engine=create_engine(f'sqlite:///{tmp_path / "db.sqlite"}',connect_args={'check_same_thread':False})
    Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine)
    with factory() as db:
        db.add(User(username='tester',password=_hash_password('test-password'),lid='test-space',role='admin')); db.commit()
    def override_db():
        with factory() as db: yield db
    main.app.dependency_overrides[get_db]=override_db
    try:
        with TestClient(main.app) as client:
            assert client.get('/health/ready').status_code == 200
            login=client.post('/login',json={'username':'tester','password':'test-password'})
            headers={'Authorization':'Bearer '+login.json()['data']['access_token']}
            first=client.post('/knowledges/createKnowledge',json={'knowledgeName':'Library A'},headers=headers).json()['data']['knowledgeID']
            second=client.post('/knowledges/createKnowledge',json={'knowledgeName':'Library B'},headers=headers).json()['data']['knowledgeID']
            pdf=fitz.open(); page=pdf.new_page(); page.insert_text((72,72),'ResearchSpace paper about quantum algorithms and experimental accuracy.'); content=pdf.tobytes(); pdf.close()
            for kid in (first,second):
                uploaded=client.post('/document/upload',data={'knowledgeID':kid},files={'documentFile':('paper.pdf',content,'application/pdf')},headers=headers)
                assert uploaded.status_code == 200, uploaded.text
            doc_id=uploaded.json()['data']['documentID']
            processor=DataProcessAgent(TestProvider(),main.app.chroma_db)
            with factory() as db:
                assert process_next_document(db,processor)
                assert sorted(row.documentStatus for row in db.query(Document).all()) == [0,2]
                assert process_next_document(db,processor)
                assert all(row.documentStatus == 2 for row in db.query(Document).all())
            before=main.app.chroma_db.chroma_db_layer1._collection.count()
            processor.add_newpaper(str(tmp_path/'pdf'/f'{doc_id}.pdf'),first)
            assert main.app.chroma_db.chroma_db_layer1._collection.count() == before
            hits=main.app.chroma_db.search_evidence('quantum algorithms',{'$and':[{'documentID':doc_id},{'knowledge_name':first}]})
            assert hits and all(hit.knowledge_id == first and hit.fusion_score for hit in hits)
            assert all(hit.chunk_id in {c.chunk_id for c in main.app.chroma_db.get_document_chunks(doc_id)} for hit in hits)
            got=client.get('/document/getFile',params={'documentID':doc_id,'knowledgeID':first},headers=headers)
            assert got.status_code == 200 and got.content.startswith(b'%PDF-')
            stream=client.post('/qa/stream',json={'question':'Hello','model':'deepseek'},headers=headers)
            assert stream.status_code == 200 and 'A test response' in stream.text
    finally:
        main.app.dependency_overrides.clear()
