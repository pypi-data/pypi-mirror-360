import json
import logging
from importlib import resources
from pathlib import Path
from typing import Any

import litellm

logger = logging.getLogger(__name__)

# Track models registered by this package.
ADDED_MODELS: list[tuple[str, str | None]] = []


DATA_DIR = Path(__file__).resolve().parent / "data"

# Directory under the user's home directory for provider cache files
USER_CACHE_DIR = Path.home() / ".cache" / "bulkllm" / "providers"


def infer_mode_from_name(name: str) -> str | None:
    """Return model mode inferred from ``name`` if it contains known keywords."""

    lowered = name.lower()
    if "tts" in lowered:
        return "audio_speech"
    if "moderation" in lowered:
        return "moderation"
    if "ocr" in lowered:
        return "ocr"
    if "embedding" in lowered or "embed" in lowered:
        return "embedding"
    return None


def get_data_file(provider: str) -> Path:
    """Return path to the cached JSON for a provider inside the package."""

    return DATA_DIR / f"{provider}.json"


def get_user_cache_file(provider: str) -> Path:
    """Return path to the user-level cached JSON for a provider."""

    return USER_CACHE_DIR / f"{provider}.json"


def load_cached_provider_data(provider: str, *, use_user_cache: bool = True) -> dict[str, Any]:
    """Load cached raw API response for ``provider``."""

    if use_user_cache:
        user_path = get_user_cache_file(provider)
        if user_path.exists():
            with open(user_path) as f:
                return json.load(f)

    resource = resources.files("bulkllm.model_registration.data").joinpath(f"{provider}.json")
    with resources.as_file(resource) as path, open(path) as f:
        return json.load(f)


def save_cached_provider_data(provider: str, data: dict[str, Any]) -> None:
    """Write raw API response for ``provider`` to cache."""

    path = get_user_cache_file(provider)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving cached provider data for {provider} to {path}")
    with open(path, "w") as f:
        json.dump(data, f)


def bulkllm_register_models(
    model_cost_map: dict[str, Any],
    warn_existing: bool = True,
    *,
    source: str | None = None,
    load_existing: bool = False,
) -> None:
    """Register multiple models with LiteLLM, warning if already present."""
    models_to_register = {}
    for model_name in model_cost_map:  # noqa: PLC0206
        model_info = None
        try:
            model_info = litellm.get_model_info(model_name)
        except Exception:  # noqa: PERF203,BLE001 - broad catch ok here
            model_info = None
        if model_info:
            if warn_existing:
                logger.debug(f"Model '{model_name}' already registered")
            if load_existing:
                models_to_register[model_name] = model_info
        else:
            logger.info(f"Registering model '{model_name}' from {source}")
            entry = (model_name, source)
            models_to_register[model_name] = model_cost_map[model_name]
            if entry not in ADDED_MODELS:
                ADDED_MODELS.append(entry)

    litellm.register_model(models_to_register)


def print_added_models() -> None:
    for model_name, model_source in ADDED_MODELS:
        print(f"{model_name} - {model_source}")
