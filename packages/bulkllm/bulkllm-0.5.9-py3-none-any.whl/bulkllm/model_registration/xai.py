import logging
import os
from functools import cache
from typing import Any

import requests

from bulkllm.model_registration.utils import (
    bulkllm_register_models,
    infer_mode_from_name,
    load_cached_provider_data,
    save_cached_provider_data,
)

logger = logging.getLogger(__name__)


def convert_xai_to_litellm(xai_model: dict[str, Any]) -> dict[str, Any] | None:
    """Convert an XAI model dict to LiteLLM format."""
    model_id = xai_model.get("id")
    if not model_id:
        logger.warning("Skipping model due to missing id: %s", xai_model)
        return None

    litellm_model_name = f"xai/{model_id}"

    model_info = {
        "litellm_provider": "xai",
        "mode": infer_mode_from_name(model_id) or "chat",
    }

    input_modalities = xai_model.get("input_modalities") or []
    output_modalities = xai_model.get("output_modalities") or []
    if "image" in input_modalities or "image" in output_modalities:
        model_info["supports_vision"] = True

    inp = xai_model.get("prompt_text_token_price")
    out = xai_model.get("completion_text_token_price")
    if inp is not None:
        model_info["input_cost_per_token"] = float(inp) / 1_000_000
    if out is not None:
        model_info["output_cost_per_token"] = float(out) / 1_000_000

    created = xai_model.get("created")
    if created is not None:
        model_info["created"] = created

    return {"model_name": litellm_model_name, "model_info": model_info}


def fetch_xai_data() -> dict[str, Any]:
    """Fetch raw model data from XAI and cache it."""
    url = "https://api.x.ai/v1/language-models"
    api_key = os.getenv("XAI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    save_cached_provider_data("xai", data)
    return data


@cache
def get_xai_models(*, use_cached: bool = True) -> dict[str, Any]:
    """Return models from the XAI list endpoint or cached data."""
    if use_cached:
        try:
            data = load_cached_provider_data("xai")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        try:
            data = fetch_xai_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch XAI models: %s", exc)
            return {}
    models: dict[str, Any] = {}
    for item in data.get("models", []):
        converted = convert_xai_to_litellm(item)
        if converted:
            info = converted["model_info"]
            name = converted["model_name"]
            models[name] = info
            for alias in item.get("aliases", []):
                models[f"xai/{alias}"] = info
    return models


@cache
def get_xai_aliases(*, use_cached: bool = True) -> set[str]:
    """Return the set of aliased XAI model names."""

    if use_cached:
        try:
            data = load_cached_provider_data("xai")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        try:
            data = fetch_xai_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch XAI models: %s", exc)
            return set()

    aliases: set[str] = set()
    for item in data.get("models", []):
        model_id = item.get("id")
        if not model_id:
            continue
        for alias in item.get("aliases", []):
            if alias != model_id:
                aliases.add(f"xai/{alias}")
    return aliases


@cache
def register_xai_models_with_litellm() -> None:
    """Fetch and register XAI models with LiteLLM."""
    bulkllm_register_models(get_xai_models(), source="xai")
