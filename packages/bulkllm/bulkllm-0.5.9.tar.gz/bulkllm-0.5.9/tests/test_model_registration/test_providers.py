import pytest
import requests

from bulkllm.model_registration import utils
from bulkllm.model_registration.anthropic import get_anthropic_models
from bulkllm.model_registration.gemini import get_gemini_models
from bulkllm.model_registration.mistral import get_mistral_models
from bulkllm.model_registration.openai import get_openai_models


@pytest.fixture(autouse=True)
def _set_user_cache_dir(monkeypatch, tmp_path):
    cache_dir = tmp_path / "providers"
    monkeypatch.setattr(utils, "USER_CACHE_DIR", cache_dir)
    return cache_dir


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self):
        return self._data


def _patch_get(monkeypatch, data):
    def fake_get(*args, **kwargs):
        return DummyResponse(data)

    monkeypatch.setattr(requests, "get", fake_get)


def test_get_openai_models_network(monkeypatch):
    sample = {"data": [{"id": "gpt-4o-mini", "object": "model", "owned_by": "openai", "permission": []}]}
    get_openai_models.cache_clear()
    _patch_get(monkeypatch, sample)
    models = get_openai_models()
    assert "openai/gpt-4o-mini" in models
    info = models["openai/gpt-4o-mini"]
    assert info["litellm_provider"] == "openai"
    assert info["mode"] == "chat"


def test_get_anthropic_models_network(monkeypatch):
    sample = {
        "data": [
            {
                "id": "claude-3-7-sonnet-20250219",
                "display_name": "Claude",
                "created_at": "2025-02-19T00:00:00Z",
                "type": "model",
            }
        ],
        "first_id": "claude-3-7-sonnet-20250219",
        "last_id": "claude-2-1",
        "has_more": True,
    }
    get_anthropic_models.cache_clear()
    _patch_get(monkeypatch, sample)
    models = get_anthropic_models()
    assert "anthropic/claude-3-7-sonnet-20250219" in models
    info = models["anthropic/claude-3-7-sonnet-20250219"]
    assert info["litellm_provider"] == "anthropic"
    assert info["mode"] == "chat"


def test_get_gemini_models_network(monkeypatch):
    sample = {
        "models": [
            {
                "name": "models/gemini-1.5-flash-001",
                "baseModelId": "gemini-1.5-flash",
                "version": "1.0",
                "displayName": "Gemini 1.5 Flash",
                "description": "High-performance LLM",
            }
        ],
        "nextPageToken": "tok",
    }
    get_gemini_models.cache_clear()
    _patch_get(monkeypatch, sample)
    models = get_gemini_models(use_cached=False)
    assert "gemini/gemini-1.5-flash-001" in models
    info = models["gemini/gemini-1.5-flash-001"]
    assert info["litellm_provider"] == "gemini"
    assert info["mode"] == "chat"


def test_get_mistral_models_network(monkeypatch):
    sample = {
        "object": "list",
        "data": [
            {
                "id": "mistral-small",
                "object": "model",
                "created": 0,
                "owned_by": "mistralai",
            }
        ],
    }
    get_mistral_models.cache_clear()
    _patch_get(monkeypatch, sample)
    models = get_mistral_models()
    assert "mistral/mistral-small" in models
    info = models["mistral/mistral-small"]
    assert info["litellm_provider"] == "mistral"
    assert info["mode"] == "chat"
