import datetime

from typer.testing import CliRunner

from bulkllm.schema import LLMConfig

LLMConfig.model_rebuild(_types_namespace={"datetime": datetime})

from bulkllm.cli import app  # noqa: E402


def test_list_models(monkeypatch):
    import litellm

    # Ensure a clean slate
    monkeypatch.setattr(litellm, "model_cost", {})

    def fake_register_models() -> None:
        litellm.model_cost["fake/model"] = {
            "litellm_provider": "openai",
            "mode": "chat",
        }

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)

    runner = CliRunner()
    result = runner.invoke(app, ["list-models"])
    assert result.exit_code == 0
    assert "fake/model" in result.output


def test_list_missing_model_configs(monkeypatch):
    from types import SimpleNamespace

    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    def fake_register_models() -> None:
        litellm.model_cost["configured/model"] = {
            "litellm_provider": "openai",
            "mode": "chat",
        }
        litellm.model_cost["unconfigured/model"] = {
            "litellm_provider": "openai",
            "mode": "chat",
        }

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr(
        "bulkllm.cli.create_model_configs",
        lambda: [SimpleNamespace(litellm_model_name="configured/model")],
    )

    runner = CliRunner()
    result = runner.invoke(app, ["list-missing-model-configs"])

    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert "unconfigured/model" in lines
    assert "configured/model" not in lines


def test_list_unique_models(monkeypatch):
    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    def fake_register_models() -> None:
        litellm.model_cost["anthropic/claude-3"] = {
            "litellm_provider": "anthropic",
            "mode": "chat",
        }
        litellm.model_cost["openrouter/anthropic/claude-3"] = {
            "litellm_provider": "openrouter",
            "mode": "chat",
        }
        litellm.model_cost["bedrock/anthropic.claude-3"] = {
            "litellm_provider": "bedrock",
            "mode": "chat",
        }

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)

    runner = CliRunner()
    result = runner.invoke(app, ["list-unique-models"])

    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines.count("anthropic/claude-3") == 1
    assert "openrouter/anthropic/claude-3" not in lines
    assert "bedrock/anthropic.claude-3" not in lines


def test_list_canonical_models(monkeypatch):
    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    monkeypatch.setattr(
        "bulkllm.model_registration.openai.get_openai_models",
        lambda: {
            "openai/gpt": {"litellm_provider": "openai", "mode": "chat", "created": 1},
            "openai/text": {"litellm_provider": "openai", "mode": "completion"},
        },
    )
    monkeypatch.setattr(
        "bulkllm.model_registration.anthropic.get_anthropic_models",
        lambda: {
            "anthropic/claude": {
                "litellm_provider": "anthropic",
                "mode": "chat",
                "created_at": "2024-01-02T00:00:00Z",
            }
        },
    )
    monkeypatch.setattr(
        "bulkllm.model_registration.gemini.get_gemini_models",
        lambda: {
            "gemini/flash": {
                "litellm_provider": "gemini",
                "mode": "chat",
            }
        },
    )
    monkeypatch.setattr(
        "bulkllm.model_registration.mistral.get_mistral_models",
        lambda: {
            "mistral/small": {
                "litellm_provider": "mistral",
                "mode": "chat",
                "created": 3,
            }
        },
    )

    def fake_register_models() -> None:
        litellm.model_cost["openai/gpt"] = {"litellm_provider": "openai", "mode": "chat"}
        litellm.model_cost["openai/text"] = {
            "litellm_provider": "openai",
            "mode": "completion",
        }
        litellm.model_cost["anthropic/claude"] = {"litellm_provider": "anthropic", "mode": "chat"}
        litellm.model_cost["gemini/flash"] = {"litellm_provider": "gemini", "mode": "chat"}
        litellm.model_cost["mistral/small"] = {"litellm_provider": "mistral", "mode": "chat"}

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr(
        "bulkllm.model_registration.canonical.create_model_configs",
        lambda: [
            LLMConfig(
                slug="gpt",
                display_name="GPT",
                company_name="openai",
                litellm_model_name="openai/gpt",
                llm_family="gpt",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 1, 1),
            ),
            LLMConfig(
                slug="claude",
                display_name="Claude",
                company_name="anthropic",
                litellm_model_name="anthropic/claude",
                llm_family="claude",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 2, 2),
            ),
            LLMConfig(
                slug="flash",
                display_name="Flash",
                company_name="gemini",
                litellm_model_name="gemini/flash",
                llm_family="flash",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 3, 3),
            ),
            LLMConfig(
                slug="small",
                display_name="Small",
                company_name="mistral",
                litellm_model_name="mistral/small",
                llm_family="small",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 4, 4),
            ),
        ],
    )

    runner = CliRunner()
    result = runner.invoke(app, ["list-canonical-models"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    rows = [line.split("|") for line in lines[2:]]  # skip header and divider
    table = {
        cells[0].strip(): (
            cells[1].strip(),
            cells[2].strip(),
            cells[3].strip(),
        )
        for cells in rows
    }

    assert table["openai/gpt"] == ("chat", "2025-01-01", "1970-01-01")
    assert table["anthropic/claude"] == (
        "chat",
        "2025-02-02",
        "2024-01-02",
    )
    assert table["gemini/flash"] == ("chat", "2025-03-03", "")
    assert table["mistral/small"] == ("chat", "2025-04-04", "1970-01-01")


def test_list_canonical_models_drops_aliases(monkeypatch):
    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    monkeypatch.setattr(
        "bulkllm.model_registration.openai.get_openai_models",
        lambda: {
            "openai/base": {"litellm_provider": "openai", "mode": "chat"},
            "openai/alias": {"litellm_provider": "openai", "mode": "chat"},
        },
    )
    monkeypatch.setattr(
        "bulkllm.model_registration.anthropic.get_anthropic_models",
        dict,
    )
    monkeypatch.setattr(
        "bulkllm.model_registration.gemini.get_gemini_models",
        dict,
    )
    monkeypatch.setattr(
        "bulkllm.model_registration.mistral.get_mistral_models",
        dict,
    )
    monkeypatch.setattr(
        "bulkllm.model_registration.openai.get_openai_aliases",
        lambda: {"openai/alias"},
    )

    def fake_register_models() -> None:
        litellm.model_cost["openai/base"] = {"litellm_provider": "openai", "mode": "chat"}
        litellm.model_cost["openai/alias"] = {"litellm_provider": "openai", "mode": "chat"}

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr(
        "bulkllm.model_registration.canonical.create_model_configs",
        lambda: [
            LLMConfig(
                slug="base",
                display_name="Base",
                company_name="openai",
                litellm_model_name="openai/base",
                llm_family="base",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 1, 1),
            ),
            LLMConfig(
                slug="alias",
                display_name="Alias",
                company_name="openai",
                litellm_model_name="openai/alias",
                llm_family="alias",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 2, 2),
            ),
        ],
    )

    runner = CliRunner()
    result = runner.invoke(app, ["list-canonical-models"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    rows = [line.split("|") for line in lines[2:]]  # skip header and divider
    table = {cells[0].strip(): cells[1].strip() for cells in rows}

    assert "openai/base" in table
    assert "openai/alias" not in table


def test_list_canonical_models_drops_mistral_aliases(monkeypatch):
    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.anthropic.get_anthropic_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.gemini.get_gemini_models", dict)
    monkeypatch.setattr(
        "bulkllm.model_registration.mistral.get_mistral_models",
        lambda: {
            "mistral/base": {"litellm_provider": "mistral", "mode": "chat"},
            "mistral/alias": {"litellm_provider": "mistral", "mode": "chat"},
        },
    )
    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_aliases", set)
    monkeypatch.setattr(
        "bulkllm.model_registration.mistral.get_mistral_aliases",
        lambda: {"mistral/alias"},
    )

    def fake_register_models() -> None:
        litellm.model_cost["mistral/base"] = {
            "litellm_provider": "mistral",
            "mode": "chat",
        }
        litellm.model_cost["mistral/alias"] = {
            "litellm_provider": "mistral",
            "mode": "chat",
        }

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr(
        "bulkllm.model_registration.canonical.create_model_configs",
        lambda: [
            LLMConfig(
                slug="base",
                display_name="Base",
                company_name="mistral",
                litellm_model_name="mistral/base",
                llm_family="base",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 1, 1),
            ),
            LLMConfig(
                slug="alias",
                display_name="Alias",
                company_name="mistral",
                litellm_model_name="mistral/alias",
                llm_family="alias",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 2, 2),
            ),
        ],
    )

    runner = CliRunner()
    result = runner.invoke(app, ["list-canonical-models"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    rows = [line.split("|") for line in lines[2:]]  # skip header and divider
    table = {cells[0].strip(): cells[1].strip() for cells in rows}

    assert "mistral/base" in table
    assert "mistral/alias" not in table


def test_list_canonical_models_prefers_id_named_model(monkeypatch):
    import litellm

    from bulkllm.model_registration import mistral

    monkeypatch.setattr(litellm, "model_cost", {})

    data = {
        "data": [
            {"id": "base", "name": "base", "aliases": ["alias"]},
            {"id": "alias", "name": "base", "aliases": ["base"]},
        ]
    }

    monkeypatch.setattr(mistral, "load_cached_provider_data", lambda *a, **k: data)
    mistral.get_mistral_models.cache_clear()
    mistral.get_mistral_aliases.cache_clear()

    monkeypatch.setattr("bulkllm.model_registration.mistral.get_mistral_models", mistral.get_mistral_models)
    monkeypatch.setattr("bulkllm.model_registration.mistral.get_mistral_aliases", mistral.get_mistral_aliases)
    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.anthropic.get_anthropic_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.gemini.get_gemini_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_aliases", set)

    def fake_register_models() -> None:
        litellm.model_cost["mistral/base"] = {"litellm_provider": "mistral", "mode": "chat"}
        litellm.model_cost["mistral/alias"] = {"litellm_provider": "mistral", "mode": "chat"}

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr(
        "bulkllm.model_registration.canonical.create_model_configs",
        lambda: [
            LLMConfig(
                slug="base",
                display_name="Base",
                company_name="mistral",
                litellm_model_name="mistral/base",
                llm_family="base",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 1, 1),
            ),
            LLMConfig(
                slug="alias",
                display_name="Alias",
                company_name="mistral",
                litellm_model_name="mistral/alias",
                llm_family="alias",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 2, 2),
            ),
        ],
    )

    runner = CliRunner()
    result = runner.invoke(app, ["list-canonical-models"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    rows = [line.split("|")[0].strip() for line in lines[2:]]

    assert "mistral/base" in rows
    assert "mistral/alias" not in rows


def test_list_canonical_models_skips_xai_fast(monkeypatch):
    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    monkeypatch.setattr(
        "bulkllm.model_registration.openai.get_openai_models",
        lambda: {
            "xai/grok-3-fast": {"litellm_provider": "xai", "mode": "chat"},
            "xai/grok-3": {"litellm_provider": "xai", "mode": "chat"},
        },
    )
    monkeypatch.setattr("bulkllm.model_registration.anthropic.get_anthropic_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.gemini.get_gemini_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.mistral.get_mistral_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_aliases", set)

    def fake_register_models() -> None:
        litellm.model_cost["xai/grok-3-fast"] = {
            "litellm_provider": "xai",
            "mode": "chat",
        }
        litellm.model_cost["xai/grok-3"] = {
            "litellm_provider": "xai",
            "mode": "chat",
        }

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.create_model_configs", list)

    runner = CliRunner()
    result = runner.invoke(app, ["list-canonical-models"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    rows = [line.split("|")[0].strip() for line in lines[2:]]

    assert "xai/grok-3" in rows
    assert "xai/grok-3-fast" not in rows


def test_list_canonical_models_drops_xai_aliases(monkeypatch):
    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.anthropic.get_anthropic_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.gemini.get_gemini_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.mistral.get_mistral_models", dict)
    monkeypatch.setattr(
        "bulkllm.model_registration.xai.get_xai_models",
        lambda: {
            "xai/base": {"litellm_provider": "xai", "mode": "chat"},
            "xai/alias": {"litellm_provider": "xai", "mode": "chat"},
        },
    )
    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_aliases", set)
    monkeypatch.setattr(
        "bulkllm.model_registration.xai.get_xai_aliases",
        lambda: {"xai/alias"},
    )

    def fake_register_models() -> None:
        litellm.model_cost["xai/base"] = {"litellm_provider": "xai", "mode": "chat"}
        litellm.model_cost["xai/alias"] = {"litellm_provider": "xai", "mode": "chat"}

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr(
        "bulkllm.model_registration.canonical.create_model_configs",
        lambda: [
            LLMConfig(
                slug="base",
                display_name="Base",
                company_name="xai",
                litellm_model_name="xai/base",
                llm_family="base",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 1, 1),
            ),
            LLMConfig(
                slug="alias",
                display_name="Alias",
                company_name="xai",
                litellm_model_name="xai/alias",
                llm_family="alias",
                temperature=1,
                max_tokens=1,
                release_date=datetime.date(2025, 2, 2),
            ),
        ],
    )

    runner = CliRunner()
    result = runner.invoke(app, ["list-canonical-models"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    rows = [line.split("|") for line in lines[2:]]  # skip header and divider
    table = {cells[0].strip(): cells[1].strip() for cells in rows}

    assert "xai/base" in table
    assert "xai/alias" not in table


def test_list_canonical_models_dedupes_gemini(monkeypatch):
    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.anthropic.get_anthropic_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.mistral.get_mistral_models", dict)
    monkeypatch.setattr("bulkllm.model_registration.openai.get_openai_aliases", set)
    monkeypatch.setattr(
        "bulkllm.model_registration.gemini.get_gemini_models",
        lambda: {
            "gemini/a": {
                "litellm_provider": "gemini",
                "mode": "chat",
                "version": "1",
            },
            "gemini/b": {
                "litellm_provider": "gemini",
                "mode": "chat",
                "version": "1",
            },
        },
    )

    def fake_register_models() -> None:
        litellm.model_cost.update(
            {
                "gemini/a": {
                    "litellm_provider": "gemini",
                    "mode": "chat",
                    "version": "1",
                },
                "gemini/b": {
                    "litellm_provider": "gemini",
                    "mode": "chat",
                    "version": "1",
                },
            }
        )

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.create_model_configs", list)

    runner = CliRunner()
    result = runner.invoke(app, ["list-canonical-models"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    rows = [line.split("|")[0].strip() for line in lines[2:]]

    assert rows.count("gemini/a") == 1
    assert "gemini/b" not in rows


def test_list_configs_estimated_cost(monkeypatch):
    from types import SimpleNamespace

    import litellm

    monkeypatch.setattr(litellm, "model_cost", {})

    def fake_register_models() -> None:
        litellm.model_cost["m"] = {"litellm_provider": "openai", "mode": "chat"}

    monkeypatch.setattr("bulkllm.cli.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.main.register_models", fake_register_models)
    monkeypatch.setattr("bulkllm.model_registration.canonical.register_models", fake_register_models)

    cfg = LLMConfig(
        slug="cfg",
        display_name="Cfg",
        company_name="ACME",
        litellm_model_name="m",
        llm_family="f",
        temperature=1,
        max_tokens=1,
    )

    monkeypatch.setattr("bulkllm.cli.create_model_configs", lambda: [cfg])
    monkeypatch.setattr("bulkllm.cli.model_resolver", lambda m: [cfg])

    monkeypatch.setattr(
        litellm,
        "get_model_info",
        lambda name: {
            "input_cost_per_token": 0.000001,
            "output_cost_per_token": 0.000002,
        },
    )

    monkeypatch.setattr(
        "bulkllm.cli.RateLimiter",
        lambda: SimpleNamespace(get_rate_limit_for_model=lambda n: SimpleNamespace(rpm=1, tpm=2)),
    )

    runner = CliRunner()
    result = runner.invoke(app, ["list-configs", "--input-tokens", "100", "--output-tokens", "50"])

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    assert "est_cost" in lines[0]
    row = [c.strip() for c in lines[2].split("|")]
    assert row[-1] == "0.00020"
