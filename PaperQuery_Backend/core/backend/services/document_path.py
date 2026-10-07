"""Resolve legacy document paths against the configured storage directories."""

import os
from pathlib import Path


def resolve_document_path(document_path: str) -> str:
    normalized = document_path.replace('\\', '/')
    filename = Path(normalized).name
    if normalized.startswith('/res/pdf/'):
        return str(Path(os.environ['PAPER_SAVE_DIR']) / filename)
    if normalized.startswith('/res/tmppdf/'):
        return str(Path(os.environ['TMP_PAPER_SAVE_DIR']) / filename)
    return str(Path(os.getenv('AcadeAgent_DIR', '.')) / normalized.lstrip('/'))
