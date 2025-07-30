import datetime

import litellm

from bulkllm.llm_configs import create_model_configs
from bulkllm.model_registration import (
    anthropic,
    gemini,
    mistral,
    openai,
    xai,
)
from bulkllm.model_registration.main import register_models

primary_providers = {"openai", "anthropic", "gemini", "xai", "qwen", "deepseek", "mistral"}


def _canonical_model_name(name: str, model_info) -> str | None:
    """Return canonical name for ``name`` dropping provider wrappers."""
    name = name.replace("/x-ai/", "/xai/")
    if name.startswith("x-ai/"):
        name = name.replace("x-ai/", "xai/")

    if model_info.get("mode") in ("image_generation", "embedding"):
        return None

    provider = model_info.get("litellm_provider")
    if provider == "text-completion-openai":
        return None

    if provider in primary_providers:
        if "ft:" in name:
            return None
        if name.startswith(f"{provider}/"):
            return name
        if "/" not in name:
            return f"{provider}/{name}"
        msg = f"Invalid model name: {name}"
        raise ValueError(msg)

    for p in primary_providers:
        if p in name:
            return None

    if name.startswith("openrouter/"):
        name = name[len("openrouter/") :]
        return name
    if name.startswith("bedrock/"):
        after = name[len("bedrock/") :]
        if "nova" not in after:
            return None
        return after

    return name


def canonical_models():
    """Return list of canonical model names."""
    unique: set[str] = set()
    for model, model_info in text_models().items():
        canonical = _canonical_model_name(model, model_info)
        if canonical is None or (canonical.startswith("xai/") and "fast" in canonical):
            continue
        unique.add(canonical)

    return sorted(unique)


def model_modes():
    register_models()
    modes: set[str] = set()
    for model, model_info in litellm.model_cost.items():
        modes.add(str(model_info.get("mode")))

    return sorted(modes)


def model_providers():
    register_models()
    providers: set[str] = set()
    for model, model_info in litellm.model_cost.items():
        providers.add(str(model_info.get("litellm_provider")))

    return sorted(providers)


def text_models():
    register_models()
    models = {}
    for model, model_info in litellm.model_cost.items():
        if model == "sample_spec":
            continue
        if "audio" in model:
            continue
        if model_info.get("mode") in ("chat", "completion"):
            if "/" not in model:
                model = f"{model_info.get('litellm_provider')}/{model}"
            models[model] = model_info

    return models


def _primary_provider_model_names():
    model_names = set()

    for model, model_info in text_models().items():
        if model_info.get("litellm_provider") in primary_providers:
            provider_name, model_name = model.split("/", 1)
            if model_name in model_names:
                print(f"ERROR: Duplicate model name: {model_name}")
            model_names.add(model_name)
    return sorted(model_names)


def get_canonical_models() -> list[list[str]]:
    """List canonical chat models with release dates."""
    register_models()

    scraped_models: dict[str, dict] = {}
    providers = [
        openai.get_openai_models,
        anthropic.get_anthropic_models,
        gemini.get_gemini_models,
        mistral.get_mistral_models,
        xai.get_xai_models,
        # openrouter.get_openrouter_models,
    ]
    for get_models in providers:
        scraped_models.update(get_models())

    def _is_xai_fast(name: str) -> bool:
        return name.startswith("xai/") and "fast" in name

    # Keep only chat models
    scraped_models = {name: info for name, info in scraped_models.items() if info.get("mode") == "chat"}

    alias_names = {
        c
        for a in openai.get_openai_aliases()
        if (c := _canonical_model_name(a, {"litellm_provider": "openai", "mode": "chat"}))
    }
    alias_names |= {
        c
        for a in mistral.get_mistral_aliases()
        if (c := _canonical_model_name(a, {"litellm_provider": "mistral", "mode": "chat"}))
    }
    alias_names |= {
        c for a in xai.get_xai_aliases() if (c := _canonical_model_name(a, {"litellm_provider": "xai", "mode": "chat"}))
    }

    canonical_scraped: dict[str, dict] = {}
    for model, model_info in scraped_models.items():
        canonical = _canonical_model_name(model, model_info)
        if canonical is None or canonical in alias_names or _is_xai_fast(canonical):
            continue
        canonical_scraped.setdefault(canonical, model_info)

    def _dedupe_gemini_by_version(models: dict[str, dict]) -> dict[str, dict]:
        seen: set[str] = set()
        deduped: dict[str, dict] = {}
        for name in sorted(models):
            info = models[name]
            if info.get("litellm_provider") == "gemini":
                version = info.get("version")
                if version and version in seen:
                    continue
                if version:
                    seen.add(version)
            deduped[name] = info
        return deduped

    canonical_scraped = _dedupe_gemini_by_version(canonical_scraped)

    canonical_registered: dict[str, dict] = {}
    for model, model_info in litellm.model_cost.items():
        if model_info.get("mode") != "chat":
            continue
        canonical = _canonical_model_name(model, model_info)
        if canonical is None or canonical in alias_names or _is_xai_fast(canonical):
            continue
        canonical_registered.setdefault(canonical, model_info)

    # Map canonical model name to release date from LLMConfig
    release_dates = {}
    for cfg in create_model_configs():
        if not cfg.release_date:
            continue
        provider = cfg.litellm_model_name.split("/", 1)[0]
        canonical = _canonical_model_name(
            cfg.litellm_model_name,
            {"mode": "chat", "litellm_provider": provider},
        )
        if canonical and canonical not in release_dates:
            release_dates[canonical] = cfg.release_date.isoformat()

    created_dates = {}
    for name, info in canonical_scraped.items():
        created = info.get("created_at", info.get("created"))
        if created is None:
            continue
        try:
            if isinstance(created, str):
                dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
            else:
                dt = datetime.datetime.fromtimestamp(int(created), tz=datetime.UTC)
            created_dates[name] = dt.date().isoformat()
        except (ValueError, OSError, OverflowError):
            created_dates[name] = str(created)

    rows = []
    for name in sorted(canonical_scraped):
        info = canonical_registered.get(name, canonical_scraped[name])
        release_date = release_dates.get(name, "")
        created = created_dates.get(name, "")
        rows.append([name, str(info.get("mode", "")), release_date, created])

    # table = _tabulate(rows, headers=["model", "mode", "release_date", "scraped_date"])
    return rows


if __name__ == "__main__":
    print(model_modes())
    print(model_providers())
    print(text_models().keys())
    print(_primary_provider_model_names())
    print(f"Total models: {len(litellm.model_cost)}")
    print(f"Total text models: {len(text_models())}")
    print(f"Total primary provider models: {len(_primary_provider_model_names())}")
