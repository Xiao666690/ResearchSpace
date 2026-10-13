"""Single document Worker; use the same configuration/indexes as main.py."""
import time
import traceback
import sys
from core.common.runtime import configure_runtime
configure_runtime()
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
from sqlalchemy import func
from core.backend.db.database import SessionLocal
from core.backend.db.models import Document, Knowledge
from core.backend.crud.crud_document import reset_stuck_documents
from core.backend.services.document_path import resolve_document_path
from core.agent.dataprocessAgent import DataProcessAgent
from core.llm.LLM import LLM
from core.retrieval.embeddings import ONNXEmbeddings
from core.vectordb.chromadb import AcadeChroma

def process_next_document(db, processor):
    document = db.query(Document).filter(Document.documentStatus == 0).order_by(Document.id).first()
    if document is None:
        return False
    identity = (document.uid, document.knowledgeID, document.lid)
    document.documentStatus = 1
    db.commit()
    try:
        result = processor.add_newpaper(resolve_document_path(document.documentPath), document.knowledgeID)
        document.documentVector = result['documentVector']
        document.primaryClassification = result['Primary Classification']
        document.secondaryClassification = result['Secondary Classification']
        document.tags = ','.join(result['Research Direction Tags'])
        document.documentDescription = result['Abstract']
        document.documentStatus = 2
        db.flush()
        knowledge = db.query(Knowledge).filter_by(knowledgeID=document.knowledgeID, lid=document.lid).first()
        if knowledge:
            count, vectors = db.query(func.count(Document.id), func.coalesce(func.sum(Document.documentVector), 0)).filter(
                Document.knowledgeID == document.knowledgeID, Document.lid == document.lid,
                Document.documentStatus == 2).one()
            knowledge.documentNum, knowledge.vectorNum = count, vectors
        db.commit()
        print(f'[worker] Indexed {identity[0]} in {identity[1]}')
        return True
    except Exception:
        db.rollback()
        row = db.query(Document).filter_by(uid=identity[0], knowledgeID=identity[1], lid=identity[2]).first()
        if row:
            row.documentStatus = 0
            db.commit()
        raise

if __name__ == '__main__':
    llm = LLM()
    chroma = AcadeChroma(os.getenv('CHROMA_LAYER1_DIR'), os.getenv('CHROMA_LAYER2_DIR'), ONNXEmbeddings(), llm)
    processor = DataProcessAgent(llm, chroma)
    with SessionLocal() as db:
        reset_stuck_documents(db)
    while True:
        try:
            with SessionLocal() as db:
                processed = process_next_document(db, processor)
            time.sleep(1 if processed else 3)
        except KeyboardInterrupt:
            break
        except Exception:
            traceback.print_exc()
            time.sleep(10)
