import importlib.util
import json
from pathlib import Path
from typing import Any, cast

import requests

from bulkllm.model_registration import (
    anthropic,
    gemini,
    mistral,
    openai,
    openrouter,
)


class DummyResponse:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def raise_for_status(self) -> None:  # pragma: no cover - dummy
        pass

    def json(self) -> dict[str, Any]:
        return self._data


def _patch_get(monkeypatch, data):
    monkeypatch.setattr(requests, "get", lambda *a, **k: DummyResponse(data))


def test_fetch_openai_data(monkeypatch):
    sample = {"data": [{"id": "b", "created": 2}, {"id": "a", "created": 1}]}
    _patch_get(monkeypatch, sample)
    saved: dict[str, Any] = {}
    monkeypatch.setattr(openai, "save_cached_provider_data", lambda p, d: saved.update(d))
    data = openai.fetch_openai_data()
    assert [m["id"] for m in data["data"]] == ["a", "b"]
    assert saved


def test_fetch_anthropic_data(monkeypatch):
    sample = {"data": [{"id": "b", "created_at": "2021"}, {"id": "a", "created_at": "2020"}]}
    _patch_get(monkeypatch, sample)
    monkeypatch.setattr(anthropic, "save_cached_provider_data", lambda p, d: None)
    data = anthropic.fetch_anthropic_data()
    assert [m["id"] for m in data["data"]] == ["a", "b"]


def test_fetch_gemini_data(monkeypatch):
    sample = {"models": [{"name": "b"}, {"name": "a"}]}
    _patch_get(monkeypatch, sample)
    monkeypatch.setattr(gemini, "save_cached_provider_data", lambda p, d: None)
    data = gemini.fetch_gemini_data()
    assert [m["name"] for m in data["models"]] == ["a", "b"]


def test_fetch_openrouter_data(monkeypatch):
    sample = {
        "data": [
            {"id": "b", "created": 1},
            {"id": "a", "created": 1},
            {"id": "c", "created": 2},
        ]
    }
    _patch_get(monkeypatch, sample)
    monkeypatch.setattr(openrouter, "save_cached_provider_data", lambda p, d: None)
    data = openrouter.fetch_openrouter_data()
    assert [m["id"] for m in data["data"]] == ["a", "b", "c"]


def test_fetch_mistral_data(monkeypatch):
    sample = {"data": [{"id": "b", "created": 2}, {"id": "a", "created": 1}]}
    _patch_get(monkeypatch, sample)
    monkeypatch.setattr(mistral, "save_cached_provider_data", lambda p, d: None)

    def _fake(p, use_user_cache=False):
        return (_ for _ in ()).throw(FileNotFoundError())

    monkeypatch.setattr(mistral, "load_cached_provider_data", _fake)
    data = mistral.fetch_mistral_data()
    assert [m["id"] for m in data["data"]] == ["a", "b"]


def test_fetch_mistral_data_uses_cached_created(monkeypatch):
    sample = {"data": [{"id": "b", "created": 3}, {"id": "a", "created": 2}]}
    cached = {"data": [{"id": "a", "created": 1}, {"id": "b", "created": 2}]}
    _patch_get(monkeypatch, sample)
    monkeypatch.setattr(mistral, "save_cached_provider_data", lambda p, d: None)
    monkeypatch.setattr(mistral, "load_cached_provider_data", lambda p, use_user_cache=False: cached)
    data = mistral.fetch_mistral_data()
    assert [m["id"] for m in data["data"]] == ["a", "b"]
    assert [m["created"] for m in data["data"]] == [1, 2]


def test_update_script_uses_helpers(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "update_model_cache",
        Path(__file__).resolve().parents[2] / "scripts" / "update_model_cache.py",
    )
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    um = cast("Any", module)

    def fake_get_data_file(provider: str) -> Path:
        return tmp_path / f"{provider}.json"

    monkeypatch.setattr(um, "get_data_file", fake_get_data_file)

    called = {}

    def _fake(provider):
        def inner():
            called[provider] = True
            return {provider: 1}

        return inner

    monkeypatch.setattr(um.openai_mod, "fetch_openai_data", _fake("openai"))
    monkeypatch.setattr(um.anthropic_mod, "fetch_anthropic_data", _fake("anthropic"))
    monkeypatch.setattr(um.gemini_mod, "fetch_gemini_data", _fake("gemini"))
    monkeypatch.setattr(um.openrouter_mod, "fetch_openrouter_data", _fake("openrouter"))
    monkeypatch.setattr(um.mistral_mod, "fetch_mistral_data", _fake("mistral"))
    monkeypatch.setattr(um, "fetch", lambda *a, **k: {})  # xai

    um.main(force=True)

    assert called.keys() == {"openai", "anthropic", "gemini", "openrouter", "mistral"}
    assert json.loads((tmp_path / "openai.json").read_text()) == {"openai": 1}
