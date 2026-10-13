"""ONNX semantic + BM25 keyword retrieval using stable source record IDs."""
from core.common.types import EvidenceChunk
from core.retrieval.sparse import BM25Retriever
from core.retrieval.fusion import reciprocal_rank_fusion

class OnnxHybridRetriever:
    def search(self, chroma, query, where, k):
        stored = chroma._collection.get(where=where, include=['documents', 'metadatas'])
        corpus = []
        lookup = {}
        for cid, text, meta in zip(stored['ids'], stored['documents'], stored['metadatas']):
            if not text or not text.strip():
                continue
            meta = meta or {}
            item = EvidenceChunk(chunk_id=meta.get('chunk_id') or cid,
                document_id=meta.get('documentID') or '',
                knowledge_id=meta.get('knowledge_name') or meta.get('knowledgeID'),
                source=meta.get('source') or '', page_number=int(meta.get('page_number') or 0), text=text)
            corpus.append(item)
            lookup[(item.document_id, item.knowledge_id, item.page_number, text)] = item
        if not corpus:
            return []
        count = min(len(corpus), max(k, 20))
        dense = []
        for doc, distance in chroma.similarity_search_with_score(query, k=count, filter=where):
            meta = doc.metadata or {}
            key = (meta.get('documentID') or '', meta.get('knowledge_name') or meta.get('knowledgeID'),
                   int(meta.get('page_number') or 0), doc.page_content)
            item = lookup.get(key)
            if item:
                dense.append(item.model_copy(update={'dense_score': float(distance)}))
        sparse = BM25Retriever(corpus).search(query, k=count)
        return reciprocal_rank_fusion([dense, sparse])[:k]
