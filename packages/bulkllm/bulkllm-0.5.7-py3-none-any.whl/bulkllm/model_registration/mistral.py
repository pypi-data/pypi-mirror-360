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


def convert_mistral_to_litellm(mistral_model: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a Mistral model dict to LiteLLM format."""
    model_id = mistral_model.get("id")
    if not model_id:
        logger.warning("Skipping model due to missing id: %s", mistral_model)
        return None

    litellm_model_name = f"mistral/{model_id}"

    model_info = {
        "litellm_provider": "mistral",
        "mode": infer_mode_from_name(model_id) or "chat",
    }

    context = mistral_model.get("max_context_length")
    if context is not None:
        model_info["max_input_tokens"] = context

    caps = mistral_model.get("capabilities", {})
    if caps.get("function_calling"):
        model_info["supports_function_calling"] = True
    if caps.get("vision"):
        model_info["supports_vision"] = True

    created = mistral_model.get("created")
    if created is not None:
        model_info["created"] = created

    return {"model_name": litellm_model_name, "model_info": model_info}


def fetch_mistral_data() -> dict[str, Any]:
    """Fetch raw model data from Mistral and cache it."""

    url = "https://api.mistral.ai/v1/models"
    api_key = os.getenv("MISTRAL_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    try:
        cached = load_cached_provider_data("mistral", use_user_cache=False)
    except FileNotFoundError:
        cached = None

    if cached:
        cached_created = {
            m.get("id"): m.get("created")
            for m in cached.get("data", [])
            if m.get("id") and m.get("created") is not None
        }

        for model in data.get("data", []):
            cid = model.get("id")
            if cid in cached_created:
                model["created"] = cached_created[cid]

    data["data"] = sorted(data.get("data", []), key=lambda m: m.get("created", 0))
    save_cached_provider_data("mistral", data)
    return data


@cache
def get_mistral_models(*, use_cached: bool = True) -> dict[str, Any]:
    """Return models from the Mistral list endpoint or cached data."""
    if use_cached:
        try:
            data = load_cached_provider_data("mistral")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        try:
            data = fetch_mistral_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch Mistral models: %s", exc)
            return {}
    models: dict[str, Any] = {}
    for item in data.get("data", []):
        converted = convert_mistral_to_litellm(item)
        if converted:
            models[converted["model_name"]] = converted["model_info"]
    return models


@cache
def register_mistral_models_with_litellm() -> None:
    """Fetch and register Mistral models with LiteLLM."""
    bulkllm_register_models(get_mistral_models(), source="mistral")


@cache
def get_mistral_aliases(*, use_cached: bool = True) -> set[str]:
    """Return the set of aliased Mistral model names."""

    if use_cached:
        try:
            data = load_cached_provider_data("mistral")
        except FileNotFoundError:
            use_cached = False
    if not use_cached:
        try:
            data = fetch_mistral_data()
        except requests.RequestException as exc:  # noqa: PERF203 - broad catch ok here
            logger.warning("Failed to fetch Mistral models: %s", exc)
            return set()

    id_map = {m.get("id"): m for m in data.get("data", []) if m.get("id")}

    aliases: set[str] = set()
    visited: set[str] = set()

    for model_id, item in id_map.items():
        if model_id in visited:
            continue

        group = set(item.get("aliases", [])) | {model_id}
        queue = list(group)
        while queue:
            name = queue.pop()
            if name in visited:
                continue
            visited.add(name)
            other = id_map.get(name)
            if other:
                for alias in other.get("aliases", []):
                    if alias not in group:
                        group.add(alias)
                        queue.append(alias)

        canonical = None
        for name in group:
            other = id_map.get(name)
            if other and other.get("name") == name:
                canonical = name
                break
        if canonical is None:
            canonical = model_id

        for name in group:
            if name != canonical:
                aliases.add(f"mistral/{name}")

    return aliases
