"""Local account/workspace service without model credentials.

Uses the original SQLAlchemy database and authentication/business routers.
Run after `python -m alembic upgrade head` with:
    python -m uvicorn local_main:app --host 127.0.0.1 --port 8001
AI routes remain unavailable; use main.py once full dependencies/keys are ready.
"""
from pathlib import Path
import os
import importlib

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
# Resolve relative paths against the backend, independent of the shell cwd.
for name in ('DB_PATH', 'PAPER_SAVE_DIR', 'TMP_PAPER_SAVE_DIR'):
    value = os.getenv(name)
    if value and not Path(value).is_absolute():
        os.environ[name] = str((ROOT / value).resolve())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.common.config import settings

app = FastAPI(title='ResearchSpace Local Account API', version='2.0.0-local')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

for module_name in (
    'user', 'system', 'dashboard', 'team', 'project', 'knowledge',
    'note', 'timeline', 'collaboration', 'studio', 'evidence_board',
):
    module = importlib.import_module(f'core.backend.router.router_{module_name}')
    app.include_router(module.router)

@app.get('/local/status')
def local_status():
    return {'service': 'researchspace-local', 'mode': 'accounts', 'ai_available': False}

@app.api_route('/{path:path}', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def unavailable(path: str):
    return JSONResponse(
        {'detail': '本地账户服务已启动。此接口需要完整后端依赖及模型配置，请配置后启动 main.py。'},
        status_code=503,
    )
