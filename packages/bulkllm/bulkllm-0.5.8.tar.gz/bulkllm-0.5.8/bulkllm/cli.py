from __future__ import annotations

from datetime import date

import litellm
import typer

from bulkllm.llm_configs import create_model_configs, model_resolver
from bulkllm.model_registration.canonical import _canonical_model_name, get_canonical_models
from bulkllm.model_registration.main import register_models
from bulkllm.rate_limiter import RateLimiter


def _tabulate(rows: list[list[str]], headers: list[str]) -> str:
    """Return a simple table for CLI output."""
    columns = list(zip(*([headers, *rows]))) if rows else [headers]
    widths = [max(len(str(c)) for c in col) for col in columns]
    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    divider = "-+-".join("-" * w for w in widths)
    lines = [fmt.format(*headers), divider]
    for row in rows:
        lines.append(fmt.format(*row))
    return "\n".join(lines)


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main_callback() -> None:
    """BulkLLM command line interface."""


@app.command("list-models")
def list_models() -> None:
    """List all models registered with LiteLLM."""
    register_models()
    for model, model_info in sorted(litellm.model_cost.items()):
        typer.echo(model)


@app.command("list-unique-models")
def list_unique_models() -> None:
    """List unique models, collapsing provider duplicates."""
    register_models()
    unique: set[str] = set()
    for model, model_info in litellm.model_cost.items():
        canonical = _canonical_model_name(model, model_info)
        if canonical is None:
            continue
        unique.add(canonical)
    for name in sorted(unique):
        typer.echo(name)

    print(f"Total unique models: {len(unique)}")


@app.command("list-canonical-models")
def list_canonical_models() -> None:
    """List canonical chat models with release dates."""
    rows = get_canonical_models()
    table = _tabulate(rows, headers=["model", "mode", "release_date", "scraped_date"])
    typer.echo(table)


@app.command("list-configs")
def list_configs(
    sort_by: str = typer.Option(
        "slug",
        "--sort-by",
        "-s",
        help="Sort by slug, company, release-date, input-cost, output-cost or cost",
        case_sensitive=False,
    ),
    model: list[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Model slugs or groups (can be repeated)",
    ),
    input_tokens: int | None = typer.Option(
        None,
        "--input-tokens",
        "-i",
        help="Input token count for cost estimation",
    ),
    output_tokens: int | None = typer.Option(
        None,
        "--output-tokens",
        "-o",
        help="Output token count for cost estimation",
    ),
) -> None:
    """List LLM configurations."""
    register_models()
    sort_key = sort_by.replace("-", "_").lower()
    key_funcs = {
        "slug": lambda c, i: c.slug,
        "company": lambda c, i: c.company_name.lower(),
        "release_date": lambda c, i: c.release_date or date.min,
        "input_cost": lambda c, i: (i.get("input_cost_per_token") or float("inf")),
        "output_cost": lambda c, i: (i.get("output_cost_per_token") or float("inf")),
        "cost": lambda c, i: (i.get("output_cost_per_token") or float("inf")),
    }
    if sort_key not in key_funcs:
        raise typer.BadParameter("Invalid sort option")

    configs = create_model_configs() if not model else model_resolver(list(model))

    config_infos = [(cfg, litellm.get_model_info(cfg.litellm_model_name)) for cfg in configs]

    config_infos = sorted(config_infos, key=lambda ci: key_funcs[sort_key](*ci))

    show_est_cost = input_tokens is not None or output_tokens is not None
    limiter = RateLimiter()
    rows = []
    for cfg, info in config_infos:
        inp = info.get("input_cost_per_token")
        out = info.get("output_cost_per_token")
        rl = limiter.get_rate_limit_for_model(cfg.litellm_model_name)
        est_cost = ""
        if show_est_cost:
            cost = 0.0
            if input_tokens is not None and inp is not None:
                cost += input_tokens * inp
            if output_tokens is not None and out is not None:
                cost += output_tokens * out
            est_cost = f"{cost:.5f}"
        row = [
            cfg.slug,
            cfg.litellm_model_name,
            cfg.company_name,
            cfg.display_name,
            cfg.release_date.isoformat() if cfg.release_date else "",
            f"{inp * 1_000_000:.2f}" if inp is not None else "",
            f"{out * 1_000_000:.2f}" if out is not None else "",
            str(rl.rpm),
            str(rl.tpm),
        ]
        if show_est_cost:
            row.append(est_cost)
        rows.append(row)

    headers = [
        "slug",
        "litellm_model_name",
        "company",
        "display_name",
        "release_date",
        "input_cost",
        "output_cost",
        "rpm",
        "tpm",
    ]
    if show_est_cost:
        headers.append("est_cost")
    table = _tabulate(rows, headers=headers)
    typer.echo(table)


@app.command("list-missing-model-configs")
def list_missing_model_configs() -> None:
    """List models without a corresponding LLMConfig."""
    register_models()
    known = {cfg.litellm_model_name for cfg in create_model_configs()}
    for model in sorted(litellm.model_cost):
        if model not in known:
            typer.echo(model)


def main() -> None:  # pragma: no cover - CLI entry point
    app()


if __name__ == "__main__":  # pragma: no cover - CLI runner
    main()
