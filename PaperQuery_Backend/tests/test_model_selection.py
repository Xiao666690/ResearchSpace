from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from core.backend.router.router_llm import get_chat_agent
from core.llm.LLM import LLM


def test_unconfigured_model_never_falls_back_to_deepseek():
    manager = object.__new__(LLM)
    manager.llms = {'deepseek': object()}

    with pytest.raises(ValueError, match='not configured'):
        manager.get_llm('kimi')
    with pytest.raises(ValueError, match='not configured'):
        manager.get_stream_llm('kimi')


def test_legacy_chat_rejects_unknown_model():
    request = SimpleNamespace(app=SimpleNamespace(chat_agents={'deepseek': object()}))
    with pytest.raises(HTTPException) as exc:
        get_chat_agent(request, 'zhipu')
    assert exc.value.status_code == 400
