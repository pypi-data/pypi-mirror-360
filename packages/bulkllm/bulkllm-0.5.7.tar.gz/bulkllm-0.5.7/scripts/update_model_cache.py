from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import requests
import typer

from bulkllm.model_registration import (
    anthropic as anthropic_mod,
    gemini as gemini_mod,
    mistral as mistral_mod,
    openai as openai_mod,
    openrouter as openrouter_mod,
)
from bulkllm.model_registration.utils import get_data_file

if TYPE_CHECKING:
    from pathlib import Path

app = typer.Typer(add_completion=False, no_args_is_help=True)


CACHE_MAX_AGE = timedelta(hours=0)


def needs_update(path: Path) -> bool:
    if not path.exists():
        return True
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return datetime.now(tz=UTC) - mtime > CACHE_MAX_AGE


def fetch(url: str, *, headers: dict[str, str] | None = None, params: dict[str, str] | None = None) -> dict:
    resp = requests.get(url, headers=headers or {}, params=params)
    resp.raise_for_status()
    return resp.json()


def write_json(path: Path, data: dict) -> None:
    """Write ``data`` to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    typer.echo(f"Updated {path}")


@app.command()
def main(force: bool = False) -> None:
    """Update cached provider responses if older than one hour."""
    # OpenAI
    openai_path = get_data_file("openai")
    if force or needs_update(openai_path):
        data = openai_mod.fetch_openai_data()
        write_json(openai_path, data)

    # XAI
    xai_path = get_data_file("xai")
    if force or needs_update(xai_path):
        headers = {}
        api_key = os.getenv("XAI_API_KEY", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            typer.echo("XAI_API_KEY is not set, skipping update")
        data = fetch("https://api.x.ai/v1/language-models", headers=headers)
        write_json(xai_path, data)

    # Anthropic
    anthropic_path = get_data_file("anthropic")
    if force or needs_update(anthropic_path):
        data = anthropic_mod.fetch_anthropic_data()
        write_json(anthropic_path, data)

    # Gemini
    gemini_path = get_data_file("gemini")
    if force or needs_update(gemini_path):
        data = gemini_mod.fetch_gemini_data()
        write_json(gemini_path, data)

    # OpenRouter
    openrouter_path = get_data_file("openrouter")
    if force or needs_update(openrouter_path):
        data = openrouter_mod.fetch_openrouter_data()
        write_json(openrouter_path, data)

    # Mistral
    mistral_path = get_data_file("mistral")
    if force or needs_update(mistral_path):
        data = mistral_mod.fetch_mistral_data()
        write_json(mistral_path, data)


if __name__ == "__main__":  # pragma: no cover - manual script
    typer.run(main)
