# bulkllm

## Enhancements over vanilla LiteLLM

bulkllm builds on top of `litellm` and adds a few extras:

- **Automatic model registration.**  The package knows how to fetch the list of
  models from OpenAI, Anthropic, Gemini and OpenRouter and registers them with
  LiteLLM.  Results are cached on disk so they can be reused offline.
- **Centralised rate limiting.**  A `RateLimiter` implementation enforces RPM,
  TPM, input and output token limits per model (or regex group) and works with
  both async and sync code.
- **Retry‑aware completion wrappers.**  Thin wrappers around
  `litellm.completion`/`acompletion` integrate Tenacity retries, rate limiting
  and usage tracking.
- **Usage tracking with statistics.**  Per‑model usage is tracked in memory with
  histograms, percentiles and cost calculations via the `UsageTracker` and
  `UsageStat` helpers.
- **Predefined LLM configurations.**  A large catalogue of model presets with
  cost information and convenient selection helpers is included.

## Development

Always run `make checku` before committing.

### Quick Commands
 - `make init` create the environment and install dependencies
 - `make help` see available commands
 - `make autoformat` format code
 - `make autoformat-unsafe` format code - including 'unsafe' fixes
 - `make lint` run linter
 - `make typecheck` run type checker
 - `make test` run tests
 - `make coverage` run tests with coverage report
 - `make check` run all checks (format, lint, typecheck, test)
 - `make checku` run all checks  (format-unsafe, lint, typecheck, test)

### Code Conventions

#### Testing
- Use **pytest** (no test classes).
- Always set `match=` in `pytest.raises`.
- Prefer `monkeypatch` over other mocks.
- Mirror the source-tree layout in `tests/`.
- Always run `make checku` after making changes.

#### Exceptions
- Catch only specific exceptions—never blanket `except:` blocks.
- Don’t raise bare `Exception`.

#### Python
- Manage env/deps with **uv** (`uv add|remove`, `uv run -- …`).
- No logging config or side-effects at import time.
- Keep interfaces (CLI, web, etc.) thin; put logic elsewhere.
- Use `typer` for CLI interfaces, `fastapi` for web interfaces, 
 and `pydantic` for data models.
