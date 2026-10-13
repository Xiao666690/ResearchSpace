"""Shared CPU embedding configuration for API and document Worker."""
import os
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from langchain_core.embeddings import Embeddings

class ONNXEmbeddings(Embeddings):
    def __init__(self):
        cache_dir = os.getenv('CHROMA_ONNX_CACHE_DIR')
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            ONNXMiniLM_L6_V2.DOWNLOAD_PATH = cache_dir
        self._ef = ONNXMiniLM_L6_V2(preferred_providers=['CPUExecutionProvider'])

    def embed_documents(self, texts):
        return self._ef(texts)

    def embed_query(self, text):
        return self._ef([text])[0]
