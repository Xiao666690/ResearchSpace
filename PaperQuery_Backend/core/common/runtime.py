"""Resolve local configuration consistently for API, Worker and scripts."""
import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[2]

def configure_runtime():
    load_dotenv(BACKEND_ROOT / '.env')
    for name in ('DB_PATH', 'PAPER_SAVE_DIR', 'TMP_PAPER_SAVE_DIR',
                 'CHROMA_LAYER1_DIR', 'CHROMA_LAYER2_DIR', 'CHROMA_ONNX_CACHE_DIR',
                 'SKILL_SANDBOX_DIR', 'BM25_INDEX_DIR', 'BGE_M3_MODEL_PATH',
                 'RERANKER_MODEL_PATH', 'ARGOS_DATA_ROOT', 'TIKTOKEN_CACHE_DIR'):
        value = os.getenv(name)
        if value and not Path(value).is_absolute():
            os.environ[name] = str((BACKEND_ROOT / value).resolve())
    os.environ.setdefault('ANONYMIZED_TELEMETRY', 'False')
    return BACKEND_ROOT
