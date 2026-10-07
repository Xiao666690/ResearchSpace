from types import SimpleNamespace

from core.vectordb.chromadb import AcadeChroma


def test_search_evidence_uses_persisted_chunk_id_when_langchain_omits_id():
    manager = object.__new__(AcadeChroma)
    manager.retrieval_enhancer = None
    paper = SimpleNamespace(id=None, page_content='Evidence on page one.', metadata={
        'documentID': 'paper-1', 'knowledge_name': 'library-1', 'page_number': 1,
    })
    manager.chroma_db_layer1 = SimpleNamespace(
        similarity_search_with_score=lambda *args, **kwargs: [(paper, 0.1)],
        _collection=SimpleNamespace(get=lambda **kwargs: {
            'ids': ['persisted-chunk-id'], 'documents': ['Evidence on page one.'],
            'metadatas': [{'documentID': 'paper-1', 'knowledge_name': 'library-1',
                           'page_number': 1}],
        }),
    )

    chunks = manager.search_evidence('Evidence', {'documentID': 'paper-1'})
    assert chunks[0].chunk_id == 'persisted-chunk-id'
