from bulkllm.rate_limiter import ModelRateLimit

RateLimitConfig = list[ModelRateLimit]


# Default rate limits - models are grouped by shared limits
DEFAULT_RATE_LIMITS: RateLimitConfig = [
    # OpenAI GPT-3.5 Turbo family
    ModelRateLimit(
        model_names=[
            "openai/gpt-3.5-turbo",
            "openai/gpt-3.5-turbo-0125",
            "openai/gpt-3.5-turbo-1106",
            "openai/gpt-3.5-turbo-16k",
            "openai/gpt-3.5-turbo-16k-0613",
        ],
        rpm=10000,
        tpm=50000000,
    ),
    # OpenAI GPT-3.5 Turbo Instruct
    ModelRateLimit(
        model_names=[
            "openai/gpt-3.5-turbo-instruct",
            "openai/gpt-3.5-turbo-instruct-0914",
        ],
        rpm=3500,
        tpm=90000,
    ),
    # OpenAI GPT-4 family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4",
            "openai/gpt-4-0613",
            "openai/gpt-4-0314",
        ],
        rpm=10000,
        tpm=1000000,
    ),
    # OpenAI GPT-4 Turbo family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4-turbo",
            "openai/gpt-4-turbo-2024-04-09",
            "openai/gpt-4-turbo-preview",
            "openai/gpt-4-0125-preview",
            "openai/gpt-4-1106-preview",
            "openai/gpt-4-1106-vision-preview",
        ],
        rpm=10000,
        tpm=2000000,
    ),
    # OpenAI GPT-4.5 Preview family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4.5-preview",
            "openai/gpt-4.5-preview-2025-02-27",
        ],
        rpm=10000,
        tpm=2000000,
    ),
    # OpenAI GPT-4.1 family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4.1",
            "openai/gpt-4.1-2025-04-14",
        ],
        rpm=10000,
        tpm=30000000,
    ),
    # OpenAI GPT-4.1-mini family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4.1-mini",
            "openai/gpt-4.1-mini-2025-04-14",
        ],
        rpm=30000,
        tpm=150000000,
    ),
    # OpenAI GPT-4.1-nano family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4.1-nano",
            "openai/gpt-4.1-nano-2025-04-14",
        ],
        rpm=30000,
        tpm=150000000,
    ),
    # OpenAI GPT-4o family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4o",
            "openai/gpt-4o-2024-05-13",
            "openai/gpt-4o-2024-08-06",
            "openai/gpt-4o-2024-11-20",
            "openai/gpt-4o-audio-preview",
            "openai/gpt-4o-audio-preview-2024-10-01",
            "openai/gpt-4o-audio-preview-2024-12-17",
        ],
        rpm=50000,
        tpm=150000000,
    ),
    # OpenAI GPT-4o-mini family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4o-mini",
            "openai/gpt-4o-mini-2024-07-18",
            "openai/gpt-4o-mini-audio-preview",
            "openai/gpt-4o-mini-audio-preview-2024-12-17",
        ],
        rpm=30000,
        tpm=150000000,
    ),
    # OpenAI GPT-4o-mini-search-preview family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4o-mini-search-preview",
            "openai/gpt-4o-mini-search-preview-2025-03-11",
        ],
        rpm=1000,
        tpm=3000000,
    ),
    # OpenAI GPT-4o-search-preview family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4o-search-preview",
            "openai/gpt-4o-search-preview-2025-03-11",
        ],
        rpm=1000,
        tpm=3000000,
    ),
    # OpenAI single models
    ModelRateLimit(model_names=["openai/gpt-4o-mini-transcribe"], rpm=10000, tpm=8000000),
    ModelRateLimit(model_names=["openai/gpt-4o-mini-tts"], rpm=10000, tpm=8000000),
    ModelRateLimit(model_names=["openai/gpt-4o-transcribe"], rpm=10000, tpm=6000000),
    ModelRateLimit(model_names=["openai/babbage-002"], rpm=3000, tpm=250000),
    ModelRateLimit(model_names=["openai/chatgpt-4o-latest"], rpm=200, tpm=500000),
    ModelRateLimit(model_names=["openai/davinci-002"], rpm=3000, tpm=250000),
    # OpenAI o1 family
    ModelRateLimit(
        model_names=[
            "openai/o1",
            "openai/o1-2024-12-17",
        ],
        rpm=10000,
        tpm=30000000,
    ),
    # OpenAI o1-mini family
    ModelRateLimit(
        model_names=[
            "openai/o1-mini",
            "openai/o1-mini-2024-09-12",
        ],
        rpm=30000,
        tpm=150000000,
    ),
    # OpenAI o1-preview family
    ModelRateLimit(
        model_names=[
            "openai/o1-preview",
            "openai/o1-preview-2024-09-12",
        ],
        rpm=10000,
        tpm=30000000,
    ),
    # OpenAI o1-pro family
    ModelRateLimit(
        model_names=[
            "openai/o1-pro",
            "openai/o1-pro-2025-03-19",
        ],
        rpm=10000,
        tpm=30000000,
    ),
    # OpenAI o3-mini family
    ModelRateLimit(
        model_names=[
            "openai/o3-mini",
            "openai/o3-mini-2025-01-31",
        ],
        rpm=30000,
        tpm=150000000,
    ),
    # OpenAI o3 family
    ModelRateLimit(
        model_names=[
            "openai/o3",
            "openai/o3-2025-04-16",
        ],
        rpm=10000,
        tpm=30000000,
        pending_timeout_seconds=600,
    ),
    # OpenAI o3-pro family
    ModelRateLimit(
        model_names=[
            "openai/o3-pro",
        ],
        rpm=10000,
        tpm=30000000,
    ),
    ModelRateLimit(
        model_names=[
            "openai/o3-pro-2025-06-10",
        ],
        rpm=10000,
        tpm=30000000,
    ),
    # OpenAI o4-mini family
    ModelRateLimit(
        model_names=[
            "openai/o4-mini",
            "openai/o4-mini-2025-04-16",
        ],
        rpm=30000,
        tpm=150000000,
    ),
    ModelRateLimit(
        model_names=["openai/codex-mini-latest"],
        rpm=30000,
        tpm=150000000,
    ),
    # Anthropic Models
    ModelRateLimit(model_names=["anthropic/claude-3-haiku-20240307"], rpm=4000, itpm=400_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-3-sonnet-20240229"], rpm=4000, itpm=400_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-3-opus-20240229"], rpm=4000, itpm=400_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-3-5-sonnet-20241022"], rpm=4000, itpm=400_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-3-5-sonnet-20240620"], rpm=4000, itpm=400_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-3-5-haiku-20241022"], rpm=4000, itpm=400_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-3-7-sonnet-20250219"], rpm=4000, itpm=200_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-opus-4-20250514"], rpm=4000, itpm=200_000, otpm=80_000),
    ModelRateLimit(model_names=["anthropic/claude-sonnet-4-20250514"], rpm=4000, itpm=200_000, otpm=80_000),
    # OpenRouter Models - use regex to match all models
    ModelRateLimit(
        model_names=["^openrouter/.*$"],
        rpm=360 * 60,
        tpm=1_000_000_000,  # OpenRouter doesn't have a token limit, so set very high
        is_regex=True,
        pending_timeout_seconds=180,
    ),
    # Gemini Models
    ModelRateLimit(
        model_names=["gemini/gemini-1.5-flash", "gemini/gemini-1.5-flash-002", "gemini/gemini-1.5-flash-001"],
        rpm=2000,
        tpm=4_000_000,
    ),
    ModelRateLimit(
        model_names=["gemini/gemini-1.5-pro", "gemini/gemini-1.5-pro-002", "gemini/gemini-1.5-pro-001"],
        rpm=1000,
        tpm=4_000_000,
    ),
    ModelRateLimit(
        model_names=[
            "gemini/gemini-2.0-flash-lite",
            "gemini/gemini-2.0-flash-lite-preview",
            "gemini/gemini-2.0-flash-lite-preview-02-05",
            "gemini/gemini-2.0-flash-lite-001",
        ],
        rpm=4000,
        tpm=4_000_000,
    ),
    ModelRateLimit(
        model_names=[
            "gemini/gemini-2.0-flash",
            "gemini/gemini-2.0-flash-001",
        ],
        rpm=2000,
        tpm=4_000_000,
    ),
    ModelRateLimit(
        model_names=[
            "gemini/gemini-2.5-flash-lite-preview-06-17",
        ],
        rpm=4000,
        tpm=4_000_000,
    ),
    ModelRateLimit(
        model_names=[
            "gemini/gemini-2.5-flash-preview-04-17",
            "gemini/gemini-2.5-flash-preview-05-20",
            "gemini/gemini-2.5-flash",
        ],
        rpm=1000,
        tpm=1_000_000,
    ),
    ModelRateLimit(
        model_names=[
            "gemini/gemini-2.5-pro-preview-03-25",
            "gemini/gemini-2.5-pro-preview-05-06",
            "gemini/gemini-2.5-pro-preview-06-05",
        ],
        rpm=150,
        tpm=2_000_000,
    ),
    # Mistral Models
    ModelRateLimit(
        model_names=["mistral/mistral-small-latest"],
        rpm=600,
        tpm=6_000_000,
    ),
    # XAI Models
    ModelRateLimit(model_names=["xai/grok-2-1212"], rpm=8 * 60, tpm=90000),
    ModelRateLimit(
        model_names=[
            "xai/grok-3-beta",
            "xai/grok-3",
        ],
        rpm=10 * 60,
    ),
    ModelRateLimit(
        model_names=[
            "xai/grok-3-mini-beta",
            "xai/grok-3-mini",
        ],
        # despite console saying 8 RPS, error message says its 3 RPS
        rpm=3 * 60,
    ),
]
