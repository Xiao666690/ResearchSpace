"""Download and verify the CPU embedding/tokenizer caches. No paid API calls."""
from core.common.runtime import configure_runtime
configure_runtime()
from core.retrieval.embeddings import ONNXEmbeddings
import tiktoken

if __name__ == '__main__':
    vector = ONNXEmbeddings().embed_query('ResearchSpace local model preparation')
    if len(vector) != 384:
        raise RuntimeError('Unexpected embedding dimensions')
    tokenizer = tiktoken.encoding_for_model('gpt-4o')
    if not tokenizer.encode('ResearchSpace'):
        raise RuntimeError('Tokenizer is unavailable')
    print('OK: ONNX CPU embedding (384 dimensions) and tokenizer cache are ready.')
