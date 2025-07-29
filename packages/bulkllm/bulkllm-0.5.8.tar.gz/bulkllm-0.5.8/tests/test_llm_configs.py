import importlib
import sys
import types

import pytest

from bulkllm.schema import LLMConfig


def _import_llm_configs(monkeypatch: pytest.MonkeyPatch):
    dummy_litellm = types.SimpleNamespace(
        get_max_tokens=lambda model: 8192,
        cost_per_token=lambda model, prompt_tokens, completion_tokens: (0.0, 0.0),
        register_model=lambda *a, **k: None,
        get_model_info=lambda *a, **k: None,
        model_cost={},
    )
    monkeypatch.setitem(sys.modules, "litellm", dummy_litellm)
    if "bulkllm.llm_configs" in sys.modules:
        del sys.modules["bulkllm.llm_configs"]
    return importlib.import_module("bulkllm.llm_configs")


@pytest.fixture
def stub_configs(monkeypatch: pytest.MonkeyPatch):
    llm_configs = _import_llm_configs(monkeypatch)
    cfg1 = LLMConfig(
        slug="cfg1",
        display_name="Cfg1",
        company_name="ACME",
        litellm_model_name="acme/cfg1",
        llm_family="cfg1",
        temperature=0.0,
        max_tokens=100,
    )
    cfg2 = LLMConfig(
        slug="cfg2",
        display_name="Cfg2",
        company_name="ACME",
        litellm_model_name="acme/cfg2",
        llm_family="cfg2",
        temperature=0.0,
        max_tokens=100,
    )
    all_cfgs = [cfg1, cfg2]
    cheap_cfgs = [cfg1]
    current_cfgs = [cfg2]
    monkeypatch.setattr(
        llm_configs, "create_model_configs", lambda system_prompt="You are a helpful AI assistant.": all_cfgs
    )
    monkeypatch.setattr(llm_configs, "cheap_model_configs", lambda: cheap_cfgs)
    monkeypatch.setattr(llm_configs, "current_model_configs", lambda: current_cfgs)
    return llm_configs, cheap_cfgs, all_cfgs, current_cfgs


def test_model_resolver_cheap(stub_configs):
    llm_configs, cheap_cfgs, _, _ = stub_configs
    result = llm_configs.model_resolver(["cheap"])
    assert result == cheap_cfgs
    assert all(isinstance(c, LLMConfig) for c in result)


def test_model_resolver_default(stub_configs):
    llm_configs, cheap_cfgs, _, _ = stub_configs
    result = llm_configs.model_resolver(["default"])
    assert result == cheap_cfgs


def test_model_resolver_all(stub_configs):
    llm_configs, _, all_cfgs, _ = stub_configs
    result = llm_configs.model_resolver(["all"])
    assert result == all_cfgs


def test_model_resolver_current(stub_configs):
    llm_configs, _, _, current_cfgs = stub_configs
    result = llm_configs.model_resolver(["current"])
    assert result == current_cfgs


def test_model_resolver_company_filter(stub_configs):
    llm_configs, _, all_cfgs, _ = stub_configs

    # Test company filtering (case insensitive)
    result = llm_configs.model_resolver(["company:acme"])
    assert result == all_cfgs  # Both cfg1 and cfg2 are from ACME

    result_upper = llm_configs.model_resolver(["company:ACME"])
    assert result_upper == all_cfgs  # Case insensitive


def test_model_resolver_company_filter_unknown(stub_configs):
    llm_configs, _, _, _ = stub_configs

    # Test unknown company
    with pytest.raises(ValueError, match="No models found for company: unknown"):
        llm_configs.model_resolver(["company:unknown"])


def test_model_resolver_individual_slugs(stub_configs):
    llm_configs, _, all_cfgs, _ = stub_configs

    # Test individual config slugs
    result = llm_configs.model_resolver(["cfg1"])
    assert len(result) == 1
    assert result[0].slug == "cfg1"

    result = llm_configs.model_resolver(["cfg2"])
    assert len(result) == 1
    assert result[0].slug == "cfg2"

    # Test multiple slugs
    result = llm_configs.model_resolver(["cfg1", "cfg2"])
    assert len(result) == 2
    assert {cfg.slug for cfg in result} == {"cfg1", "cfg2"}


def test_model_resolver_unknown_slug(stub_configs):
    llm_configs, _, _, _ = stub_configs

    with pytest.raises(ValueError, match="Unknown model config: unknown_slug"):
        llm_configs.model_resolver(["unknown_slug"])
