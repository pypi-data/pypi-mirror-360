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


def convert_gemini_to_litellm(gemini_model: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a Gemini model dict to LiteLLM format."""
    name = gemini_model.get("name")
    if not name:
        logger.warning("Skipping model due to missing name: %s", gemini_model)
        return None

    model_id = name.split("/")[-1]
    litellm_model_name = f"gemini/{model_id}"

    model_info = {
        "litellm_provider": "gemini",
        "mode": infer_mode_from_name(name) or "chat",
    }

    token_limit = gemini_model.get("tokenLimit")
    if token_limit is not None:
        model_info["max_tokens"] = token_limit

    input_limit = gemini_model.get("inputTokenLimit")
    if input_limit is not None:
        model_info["max_input_tokens"] = input_limit

    output_limit = gemini_model.get("outputTokenLimit")
    if output_limit is not None:
        model_info["max_output_tokens"] = output_limit

    generation_methods = gemini_model.get("supportedGenerationMethods")
    if generation_methods is None:
        generation_methods = gemini_model.get("supported_generation_methods", [])

    if "countTokens" in generation_methods:
        model_info["supports_prompt_caching"] = True

    version = gemini_model.get("version")
    if version is not None:
        model_info["version"] = version

    return {"model_name": litellm_model_name, "model_info": model_info}


def fetch_gemini_data() -> dict[str, Any]:
    """Fetch raw model data from Google Gemini and cache it."""

    api_key = os.getenv("GEMINI_API_KEY", "")
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    params = {"key": api_key} if api_key else None

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    data["models"] = sorted(data.get("models", []), key=lambda m: m.get("name", ""))
    save_cached_provider_data("gemini", data)
    return data


@cache
def get_gemini_models(*, use_cached: bool = True) -> dict[str, Any]:
    """Return models from the Google Gemini list endpoint or cached data."""
    if use_cached:
        try:
            data = load_cached_provider_data("gemini")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        try:
            data = fetch_gemini_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch Gemini models: %s", exc)
            return {}
    models: dict[str, Any] = {}
    for item in data.get("models", []):
        converted = convert_gemini_to_litellm(item)
        if converted:
            models[converted["model_name"]] = converted["model_info"]
    return models


@cache
def register_gemini_models_with_litellm() -> None:
    """Fetch and register Gemini models with LiteLLM."""
    bulkllm_register_models(get_gemini_models(), source="gemini")
