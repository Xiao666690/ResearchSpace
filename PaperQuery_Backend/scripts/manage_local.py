"""Manage only this checkout's local API, document Worker and Vite processes."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import httpx
import psutil
from core.common.runtime import configure_runtime, BACKEND_ROOT
configure_runtime()

ROOT=BACKEND_ROOT.parent
FRONTEND=ROOT/'PaperQuery_Frontend'
PYTHON=BACKEND_ROOT/'.venv/Scripts/python.exe'
STATE=BACKEND_ROOT/'res/local-services.json'

def owned(process):
    try:
        directory=Path(process.cwd()).resolve()
        command=' '.join(process.cmdline())
        backend=directory == BACKEND_ROOT and any(x in command for x in ('main:app','local_main:app','vector.py'))
        frontend=directory == FRONTEND and 'vite' in command
        return backend or frontend
    except (psutil.Error,OSError):
        return False

def stop_process(process):
    if not owned(process):
        raise RuntimeError('Refusing to stop a process outside this checkout')
    children=process.children(recursive=True)
    for child in reversed(children):
        try: child.terminate()
        except psutil.NoSuchProcess: pass
    try: process.terminate()
    except psutil.NoSuchProcess: pass
    _,alive=psutil.wait_procs(children+[process],timeout=5)
    for item in alive:
        try: item.kill()
        except psutil.NoSuchProcess: pass

def on_port(port):
    for connection in psutil.net_connections(kind='tcp'):
        if connection.status == psutil.CONN_LISTEN and connection.laddr.port == port and connection.pid:
            return psutil.Process(connection.pid)
    return None

def tracked():
    if not STATE.exists(): return {}
    return json.loads(STATE.read_text(encoding='utf-8'))

def save(state):
    STATE.parent.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(state,indent=2),encoding='utf-8')

def stop():
    state=tracked()
    targets=[]
    for data in state.values():
        try:
            process=psutil.Process(data['pid'])
            if abs(process.create_time()-data['created'])<1 and owned(process): targets.append(process)
        except psutil.NoSuchProcess: pass
    # Also adopt this checkout's older account-only server if it is listening.
    for port in (8001,8080):
        process=on_port(port)
        if process and owned(process): targets.append(process)
    # Root process first, so its descendants are reaped together.
    seen=set()
    for process in targets:
        if process.pid in seen or not process.is_running(): continue
        seen.add(process.pid)
        stop_process(process)
    save({})

def launch(name,arguments,directory):
    log=open(directory/f'{name}.log','ab',buffering=0)
    error=open(directory/f'{name}-error.log','ab',buffering=0)
    try:
        process=subprocess.Popen(arguments,cwd=directory,stdout=log,stderr=error,
            env={**os.environ,'PYTHONUTF8':'1','PYTHONUNBUFFERED':'1'},
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    finally: log.close(); error.close()
    return {'pid':process.pid,'created':psutil.Process(process.pid).create_time()}

def wait_http(url,expected):
    with httpx.Client(trust_env=False,timeout=2) as client:
        for _ in range(120):
            try:
                response=client.get(url)
                if response.status_code == 200 and expected(response): return
            except httpx.HTTPError: pass
            time.sleep(.25)
    raise RuntimeError('Service did not become available. Check full-api-error.log or vite-local-error.log.')

def start():
    state=tracked()
    api=on_port(8001)
    if api and not owned(api): raise RuntimeError('Port 8001 belongs to another project; stop it manually or change the port.')
    if api:
        with httpx.Client(trust_env=False,timeout=3) as client:
            title=client.get('http://127.0.0.1:8001/openapi.json').json()['info']['title']
        if title != 'ResearchSpace API':
            stop_process(api); api=None
    if api is None:
        state['api']=launch('full-api',[str(PYTHON),'-m','uvicorn','main:app','--host','127.0.0.1','--port','8001'],BACKEND_ROOT)
        save(state)
    wait_http('http://127.0.0.1:8001/health/live',lambda r:r.json().get('service')=='paperagent-api')
    if os.getenv('DEEPSEEK_API_KEY','').strip():
        worker=state.get('worker')
        running=False
        if worker:
            try:
                process=psutil.Process(worker['pid'])
                running=abs(process.create_time()-worker['created'])<1 and owned(process)
            except psutil.NoSuchProcess: pass
        if not running:
            state['worker']=launch('vector-worker',[str(PYTHON),'vector.py'],BACKEND_ROOT); save(state)
    frontend=on_port(8080)
    if frontend and not owned(frontend): raise RuntimeError('Port 8080 belongs to another project; refusing to replace it.')
    if frontend is None:
        node=shutil.which('node.exe') or shutil.which('node')
        if node is None: raise RuntimeError('Node.js is unavailable')
        state['frontend']=launch('vite-local',[node,'node_modules/vite/bin/vite.js','--mode','dev','--host','127.0.0.1','--port','8080','--strictPort'],FRONTEND); save(state)
    wait_http('http://127.0.0.1:8080/login',lambda r:'/@vite/client' in r.text)
    print('Frontend: http://127.0.0.1:8080/login')
    print('Full API: http://127.0.0.1:8001/docs')
    print('AI: configured' if os.getenv('DEEPSEEK_API_KEY','').strip() else 'AI: fill DEEPSEEK_API_KEY in PaperQuery_Backend/.env, then run start_all.ps1 again.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['start','restart','stop','status']); action=parser.parse_args().action
    if action in ('restart','stop'): stop()
    if action in ('start','restart'): start()
    if action=='status':
        for port in (8001,8080):
            process=on_port(port); print(port, 'running (this project)' if process and owned(process) else 'stopped or other project')
