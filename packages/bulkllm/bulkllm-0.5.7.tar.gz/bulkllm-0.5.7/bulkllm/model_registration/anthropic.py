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


def convert_anthropic_to_litellm(anthropic_model: dict[str, Any]) -> dict[str, Any] | None:
    """Convert an Anthropic model dict to LiteLLM format."""
    model_id = anthropic_model.get("id")
    if not model_id:
        logger.warning("Skipping model due to missing id: %s", anthropic_model)
        return None

    litellm_model_name = f"anthropic/{model_id}"

    context_length = anthropic_model.get("context_window") or anthropic_model.get("context_length")
    max_tokens = anthropic_model.get("max_tokens") or anthropic_model.get("max_output_tokens")

    model_info = {
        "litellm_provider": "anthropic",
        "mode": infer_mode_from_name(model_id) or "chat",
    }
    if context_length is not None:
        model_info["max_input_tokens"] = context_length
    if max_tokens is not None:
        model_info["max_tokens"] = max_tokens
        model_info.setdefault("max_output_tokens", max_tokens)

    for extra_field in ["deprecation_date", "display_name", "created_at"]:
        value = anthropic_model.get(extra_field)
        if value is not None:
            model_info[extra_field] = value

    return {"model_name": litellm_model_name, "model_info": model_info}


def fetch_anthropic_data() -> dict[str, Any]:
    """Fetch raw model data from Anthropic and cache it."""

    url = "https://api.anthropic.com/v1/models"
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    data["data"] = sorted(data.get("data", []), key=lambda m: m.get("created_at", ""))
    save_cached_provider_data("anthropic", data)
    return data


@cache
def get_anthropic_models(*, use_cached: bool = True) -> dict[str, Any]:
    """Return models from the Anthropic list endpoint or cached data."""
    if use_cached:
        try:
            data = load_cached_provider_data("anthropic")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        try:
            data = fetch_anthropic_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch Anthropic models: %s", exc)
            return {}
    models: dict[str, Any] = {}
    for item in data.get("data", []):
        converted = convert_anthropic_to_litellm(item)
        if converted:
            models[converted["model_name"]] = converted["model_info"]
    return models


@cache
def register_anthropic_models_with_litellm() -> None:
    """Fetch and register Anthropic models with LiteLLM."""
    bulkllm_register_models(get_anthropic_models(), source="anthropic")
