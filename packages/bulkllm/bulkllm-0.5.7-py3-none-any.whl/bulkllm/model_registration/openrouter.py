import json
import logging
import time
from functools import cache
from pathlib import Path
from typing import Any

import litellm
import requests

from bulkllm.model_registration.utils import (
    bulkllm_register_models,
    infer_mode_from_name,
    load_cached_provider_data,
    save_cached_provider_data,
)

logger = logging.getLogger(__name__)


def get_cache_file_path() -> Path:
    """Returns the path to the cache file."""
    cache_dir = Path.home() / ".cache" / "bulkllm"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "openrouter_models_cache.json"


def read_cache() -> dict[str, Any] | None:
    """Read cached OpenRouter models if available and not expired."""
    cache_file = get_cache_file_path()

    if not cache_file.exists():
        return None

    with open(cache_file) as f:
        cache_data = json.load(f)

    # Check if cache is expired (older than 24 hours)
    cache_timestamp = cache_data.get("timestamp", 0)
    cache_age = time.time() - cache_timestamp
    cache_max_age = 24 * 60 * 60  # 24 hours in seconds

    if cache_age > cache_max_age:
        return None

    return cache_data.get("models")


def write_cache(models: dict[str, Any]) -> None:
    """Write OpenRouter models to cache with current timestamp."""
    cache_file = get_cache_file_path()

    try:
        cache_data = {"timestamp": time.time(), "models": models}

        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
    except Exception as e:  # noqa
        logger.warning("Error writing cache: %s", e)


def fetch_openrouter_data() -> dict[str, Any]:
    """Fetch raw model data from OpenRouter and cache it."""

    url = "https://openrouter.ai/api/v1/models"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    data["data"] = sorted(data.get("data", []), key=lambda m: (m.get("created", 0), m.get("id")))
    save_cached_provider_data("openrouter", data)
    return data


@cache
def get_openrouter_models(*, use_cached: bool = True) -> dict[str, Any]:
    if use_cached:
        try:
            models_data = load_cached_provider_data("openrouter")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        cached_models = read_cache()
        if cached_models is not None:
            return cached_models
        try:
            models_data = fetch_openrouter_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch OpenRouter models (offline mode?): %s", exc)
            return {}

    litellm_models = {}
    for model in models_data.get("data", []):
        converted_model = convert_openrouter_to_litellm(model)

        if converted_model:
            litellm_models[converted_model["model_name"]] = converted_model["model_info"]

    # Cache the results
    write_cache(litellm_models)

    return litellm_models


@cache
def register_openrouter_models_with_litellm():
    """Register models retrieved from OpenRouter."""
    litellm_model_names_pre_registration = set(litellm.model_cost.keys())
    litellm_models = get_openrouter_models()
    model_names_for_registration = set(litellm_models.keys())
    bulkllm_register_models(litellm_models, source="openrouter")

    litellm_model_names_post_registration = set(litellm.model_cost.keys())

    failed_to_register = model_names_for_registration - litellm_model_names_post_registration
    successfully_registered = litellm_model_names_post_registration - litellm_model_names_pre_registration

    logger.info(
        "Registered %s models successfully",
        len(successfully_registered),
    )
    logger.info(
        "Failed to register %s models",
        len(failed_to_register),
    )
    logger.info("Failed to register models: %s", failed_to_register)


def convert_openrouter_to_litellm(openrouter_model: dict[str, Any]) -> dict[str, Any] | None:
    """Converts an OpenRouter model dictionary to the LiteLLM format."""

    model_id = openrouter_model.get("id")
    if not model_id:
        logger.warning(
            "Skipping model due to missing id: %s",
            openrouter_model.get("name", "Unknown"),
        )
        return None

    litellm_model_name = f"openrouter/{model_id}"

    architecture = openrouter_model.get("architecture", {})
    input_modalities: list[str] = architecture.get("input_modalities", [])
    output_modalities: list[str] = architecture.get("output_modalities", [])

    # Determine mode
    mode = "chat"  # Default
    if "text" in input_modalities and "image" in output_modalities:
        mode = "image_generation"
    elif "text" in input_modalities and "audio" in output_modalities:
        mode = "audio_speech"
    elif "audio" in input_modalities and "text" in output_modalities:
        mode = "audio_transcription"
    elif "image" in input_modalities and "text" in output_modalities:
        mode = "vision"  # LiteLLM uses supports_vision flag, but map mode if possible
    elif "text" not in input_modalities and "text" not in output_modalities:
        # Attempt to infer from modality string if input/output lists are empty/missing
        modality_str = architecture.get("modality", "")
        if "text->image" in modality_str:
            mode = "image_generation"
        elif "text->audio" in modality_str:
            mode = "audio_speech"
        elif "audio->text" in modality_str:
            mode = "audio_transcription"
        elif "image->text" in modality_str:
            mode = "vision"

    keyword_mode = infer_mode_from_name(model_id)
    if keyword_mode is not None:
        mode = keyword_mode

    pricing = openrouter_model.get("pricing", {})
    input_cost = float(pricing.get("prompt", 0.0))
    output_cost = float(pricing.get("completion", 0.0))

    context_length = openrouter_model.get("context_length")
    top_provider = openrouter_model.get("top_provider", {})
    max_completion_tokens = top_provider.get("max_completion_tokens")

    max_input_tokens = context_length
    # Use max_completion_tokens if available, otherwise fallback to context_length
    max_output_tokens = max_completion_tokens if max_completion_tokens is not None else context_length
    # LiteLLM legacy 'max_tokens': prefer max_output, then max_input
    max_tokens = max_output_tokens if max_output_tokens is not None else max_input_tokens

    supports_vision = "image" in input_modalities
    supports_audio_input = "audio" in input_modalities
    supports_audio_output = "audio" in output_modalities
    supports_web_search = float(pricing.get("web_search", 0.0)) > 0
    # Assume True for chat models, False otherwise. OpenRouter doesn't specify this directly.
    supports_system_messages = mode == "chat"

    # Fields not directly available from OpenRouter API for basic models endpoint
    supports_function_calling = False  # Assume False
    supports_parallel_function_calling = False  # Assume False
    supports_prompt_caching = False  # Assume False
    supports_response_schema = False  # Assume False

    model_info = {
        "max_tokens": max_tokens,
        "max_input_tokens": max_input_tokens,
        "max_output_tokens": max_output_tokens,
        "input_cost_per_token": input_cost,
        "output_cost_per_token": output_cost,
        "litellm_provider": "openrouter",
        "mode": mode,
        "supports_function_calling": supports_function_calling,
        "supports_parallel_function_calling": supports_parallel_function_calling,
        "supports_vision": supports_vision,
        "supports_audio_input": supports_audio_input,
        "supports_audio_output": supports_audio_output,
        "supports_prompt_caching": supports_prompt_caching,
        "supports_response_schema": supports_response_schema,
        "supports_system_messages": supports_system_messages,
        "supports_web_search": supports_web_search,
        # "search_context_cost_per_query": search_context_cost_per_query, # Omit if None
        # "deprecation_date": deprecation_date # Omit if None
    }
    created = openrouter_model.get("created")
    if created is not None:
        model_info["created"] = created
    # Clean None values from model_info
    model_info = {k: v for k, v in model_info.items() if v is not None}

    return {"model_name": litellm_model_name, "model_info": model_info}
