import json
import logging
import os
from functools import cache
from importlib import resources
from typing import Any

import requests

from bulkllm.model_registration.utils import (
    bulkllm_register_models,
    infer_mode_from_name,
    load_cached_provider_data,
    save_cached_provider_data,
)

logger = logging.getLogger(__name__)


def _load_detailed_data() -> dict[str, Any]:
    """Return the bundled OpenAI detailed JSON."""

    resource = resources.files("bulkllm.model_registration.data").joinpath("openai_detailed.json")
    with resources.as_file(resource) as path, open(path) as f:
        return json.load(f)


@cache
def _get_detailed_lookup() -> dict[str, dict[str, Any]]:
    """Return mapping of model slug to detailed info."""

    data = _load_detailed_data()
    lookup: dict[str, dict[str, Any]] = {}

    for item in data.get("modalities", []):
        slug = item.get("name")
        if slug:
            lookup.setdefault(slug, {})["modalities"] = item

    for item in data.get("pricing", []):
        base_slugs = set()
        if item.get("current_snapshot"):
            base_slugs.add(item["current_snapshot"])
        if item.get("name"):
            base_slugs.add(item["name"])

        snapshots = item.get("snapshots") or []
        for snap in snapshots:
            if isinstance(snap, str):
                snap_name = snap
                snap_values = None
            else:
                snap_name = snap.get("name")
                snap_values = snap.get("values")
            if snap_name:
                base_slugs.add(snap_name)
                snap_item = {**item, "current_snapshot": snap_name}
                if snap_values is not None:
                    snap_item["values"] = snap_values
                lookup.setdefault(snap_name, {})["pricing"] = snap_item

        for slug in base_slugs:
            lookup.setdefault(slug, {})["pricing"] = item

    for item in data.get("rate_limits", []):
        slug = item.get("name")
        if slug:
            lookup.setdefault(slug, {})["rate_limits"] = item

    return lookup


def convert_openai_to_litellm(openai_model: dict[str, Any]) -> dict[str, Any] | None:
    """Convert an OpenAI model dict to LiteLLM format."""
    model_id = openai_model.get("id")
    if not model_id:
        logger.warning("Skipping model due to missing id: %s", openai_model)
        return None

    litellm_model_name = f"openai/{model_id}"

    model_info = {
        "litellm_provider": "openai",
        "mode": infer_mode_from_name(model_id) or "chat",
    }

    for field in ["object", "created", "owned_by", "root", "parent"]:
        value = openai_model.get(field)
        if value is not None:
            model_info[field] = value

    return {"model_name": litellm_model_name, "model_info": model_info}


def _convert_detailed_to_litellm(slug: str, data: dict[str, Any]) -> dict[str, Any]:
    """Convert bundled detailed info for one model."""

    model_info: dict[str, Any] = {
        "litellm_provider": "openai",
        "mode": infer_mode_from_name(slug) or "chat",
    }

    modalities = data.get("modalities")
    if modalities:
        mods_in = modalities.get("modalities", {}).get("input", [])
        mods_out = modalities.get("modalities", {}).get("output", [])

        if "image" in mods_out and "text" in mods_in:
            model_info["mode"] = "image_generation"
        elif "audio" in mods_in and "text" in mods_out:
            model_info["mode"] = "audio_transcription"
        elif "text" in mods_in and "audio" in mods_out:
            model_info["mode"] = "audio_speech"

        if "image" in mods_in or "image" in mods_out:
            model_info["supports_vision"] = True
        if "audio" in mods_in:
            model_info["supports_audio_input"] = True
        if "audio" in mods_out:
            model_info["supports_audio_output"] = True

        context = modalities.get("context_window")
        if context is not None:
            model_info["max_input_tokens"] = context

        max_output = modalities.get("max_output_tokens")
        if max_output is not None:
            model_info["max_output_tokens"] = max_output

        supported = set(modalities.get("supported_features", []))
        if "streaming" in supported:
            model_info["supports_prompt_caching"] = True
        if "function_calling" in supported:
            model_info["supports_function_calling"] = True
            model_info["supports_parallel_function_calling"] = True

        if modalities.get("reasoning_tokens"):
            model_info["supports_reasoning"] = True

        price_data = modalities.get("price_data", {}).get("main", {})
        if price_data:
            inp = price_data.get("input")
            out = price_data.get("output")
            reasoning = price_data.get("reasoning")
            if inp is not None:
                model_info["input_cost_per_token"] = float(inp) / 1_000_000
            if out is not None:
                model_info["output_cost_per_token"] = float(out) / 1_000_000
            if reasoning is not None:
                model_info["output_cost_per_reasoning_token"] = float(reasoning) / 1_000_000

    pricing = data.get("pricing")
    if pricing:
        values = pricing.get("values", {}).get("main", {})
        if values:
            inp = values.get("input")
            out = values.get("output")
            reasoning = values.get("reasoning")
            if inp is not None:
                model_info["input_cost_per_token"] = float(inp) / 1_000_000
            if out is not None:
                model_info["output_cost_per_token"] = float(out) / 1_000_000
            if reasoning is not None:
                model_info["output_cost_per_reasoning_token"] = float(reasoning) / 1_000_000

        if pricing.get("deprecation_date"):
            model_info["deprecation_date"] = pricing["deprecation_date"]

    rl = data.get("rate_limits")
    if rl:
        if isinstance(rl.get("rate_limits"), list):
            rl_entry = rl.get("rate_limits")[0] if rl.get("rate_limits") else {}
            tiers = rl_entry.get("rate_limits", {})
        else:
            tiers = rl.get("rate_limits", {})
        tier1 = tiers.get("tier_1", {})
        rpm = tier1.get("rpm")
        tpm = tier1.get("tpm")
        if rpm is not None:
            model_info["rpm"] = rpm
        if tpm is not None:
            model_info["tpm"] = tpm

    keyword_mode = infer_mode_from_name(slug)
    if keyword_mode is not None:
        model_info["mode"] = keyword_mode

    model_info = {k: v for k, v in model_info.items() if v is not None}
    return {"model_name": f"openai/{slug}", "model_info": model_info}


def fetch_openai_data() -> dict[str, Any]:
    """Fetch raw model data from OpenAI and cache it."""

    url = "https://api.openai.com/v1/models"
    api_key = os.getenv("OPENAI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    data["data"] = sorted(data.get("data", []), key=lambda m: m.get("created", 0))
    save_cached_provider_data("openai", data)
    return data


@cache
def get_openai_models(*, use_cached: bool = True) -> dict[str, Any]:
    """Return models from the OpenAI list endpoint or cached data."""
    if use_cached:
        try:
            data = load_cached_provider_data("openai")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        try:
            data = fetch_openai_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch OpenAI models: %s", exc)
            return {}
    models: dict[str, Any] = {}
    for item in data.get("data", []):
        converted = convert_openai_to_litellm(item)
        if converted:
            models[converted["model_name"]] = converted["model_info"]

    for slug, details in _get_detailed_lookup().items():
        converted = _convert_detailed_to_litellm(slug, details)
        models[converted["model_name"]] = {
            **models.get(converted["model_name"], {}),
            **converted["model_info"],
        }

    return models


@cache
def register_openai_models_with_litellm() -> None:
    """Fetch and register OpenAI models with LiteLLM."""
    bulkllm_register_models(get_openai_models(), source="openai")


@cache
def get_openai_aliases() -> set[str]:
    """Return the set of aliased OpenAI model names."""

    aliases: set[str] = set()
    data = _load_detailed_data()
    for section in ("pricing", "rate_limits"):
        for item in data.get(section, []):
            name = item.get("name")
            if not name:
                continue
            snapshot = item.get("current_snapshot")
            if snapshot and str(snapshot) != name:
                aliases.add(f"openai/{name}")

    # Some legacy models appear in the simple model list but not in the
    # detailed data. If a versioned variant exists, treat the base name as an
    # alias. This dedupes entries like ``gpt-3.5-turbo-16k`` which maps to
    # ``gpt-3.5-turbo-16k-0613``.
    try:
        simple = load_cached_provider_data("openai", use_user_cache=False)
    except (FileNotFoundError, json.JSONDecodeError):  # noqa: PERF203 - best effort
        simple = {}
    detailed_slugs = set(_get_detailed_lookup().keys())
    for item in simple.get("data", []):
        model_id = item.get("id")
        if not model_id:
            continue
        for slug in detailed_slugs:
            if slug.startswith(f"{model_id}-"):
                aliases.add(f"openai/{model_id}")
                break

    return aliases
