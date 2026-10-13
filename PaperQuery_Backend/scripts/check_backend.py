"""Local configuration check; --check-api explicitly makes one small provider call."""
import argparse
import json
import os
from pathlib import Path
from core.common.runtime import configure_runtime, BACKEND_ROOT
configure_runtime()

def run(check_api=False):
    from sqlalchemy import text
    from core.backend.db.database import SessionLocal
    from core.retrieval.embeddings import ONNXEmbeddings
    from core.llm.LLM import LLM
    import main
    with SessionLocal() as db:
        db.execute(text('SELECT 1'))
    vector = ONNXEmbeddings().embed_query('ResearchSpace backend check')
    assert len(vector) == 384
    configured = bool(os.getenv('DEEPSEEK_API_KEY','').strip())
    report = {'database': 'ok', 'embedding_dimensions': len(vector),
              'api_routes': len(main.app.routes), 'deepseek_key_configured': configured,
              'model': os.getenv('DEEPSEEK_MODEL'), 'translation': os.getenv('TRANSLATION_PROVIDER'),
              'live_api_verified': False}
    if configured:
        manager = LLM()
        report['configured_models'] = sorted(manager.get_all_llms())
        if check_api:
            reply = manager.get_llm('deepseek').invoke('Reply with only OK.', max_tokens=8)
            if not reply.content.strip():
                raise RuntimeError('Provider returned an empty response')
            report['live_api_verified'] = True
    elif check_api:
        raise RuntimeError('Fill DEEPSEEK_API_KEY in PaperQuery_Backend/.env first.')
    target = BACKEND_ROOT / 'res/backend-check.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-api',action='store_true',help='Make one paid API request to verify the configured key/model')
    args=parser.parse_args()
    try:
        run(args.check_api)
    except Exception as error:
        # Never print request headers, API keys, or the complete environment.
        print('CHECK FAILED:', type(error).__name__, 'Check local logs/configuration; credentials are not printed.')
        raise SystemExit(1)
