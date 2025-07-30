from litellm import Usage
from litellm.utils import supports_reasoning

from bulkllm.usage_tracker import convert_litellm_usage_to_usage_record


def test_grok3mini_usage_consistency() -> None:  # noqa: D103 - test name is descriptive
    model_name = "xai/grok-3-mini"
    assert supports_reasoning(model_name)

    usage_raw = {
        "completion_tokens": 2,
        "completion_tokens_details": {
            "accepted_prediction_tokens": 0,
            "audio_tokens": 0,
            "reasoning_tokens": 393,
            "rejected_prediction_tokens": 0,
            "text_tokens": None,
        },
        "prompt_tokens": 12,
        "prompt_tokens_details": {"audio_tokens": 0, "cached_tokens": 3, "image_tokens": 0, "text_tokens": 12},
        "total_tokens": 407,
    }
    usage_raw = Usage(**usage_raw)
    usage_record = convert_litellm_usage_to_usage_record(usage_raw, model=model_name)

    assert usage_record.input_tokens_total == 12
    assert usage_record.input_text_tokens == 12
    assert usage_record.input_cached_tokens == 3
    assert usage_record.output_tokens_total == 395

    assert usage_record.tokens_total == 407

    assert usage_record.is_valid, f"Usage inconsistencies detected: {usage_record.inconsistencies}"


def test_prompt_cache_usage_interpretation_anthropic_first_call():
    usage_data = {
        "completion_tokens": 110,
        "prompt_tokens": 18,
        "total_tokens": 128,
        "completion_tokens_details": None,
        "prompt_tokens_details": {"audio_tokens": None, "cached_tokens": 0, "text_tokens": None, "image_tokens": None},
        "cache_creation_input_tokens": 2600,
        "cache_read_input_tokens": 0,
    }
    litellm_usage = Usage(**usage_data)
    usage_record = convert_litellm_usage_to_usage_record(litellm_usage, model="anthropic/claude-3-5-sonnet-20240620")
    print(usage_record)
    assert usage_record.is_valid, f"Usage inconsistencies detected: {usage_record.inconsistencies}"
    assert usage_record.tokens_total == 18 + 110 + 2600
    assert usage_record.input_tokens_total == 18 + 2600
    assert usage_record.input_cached_tokens == 0
    assert usage_record.cache_creation_input_tokens == 2600


def test_prompt_cache_usage_interpretation_anthropic_second_call():
    usage_data = {
        "completion_tokens": 115,
        "prompt_tokens": 2629,
        "total_tokens": 2744,
        "completion_tokens_details": None,
        "prompt_tokens_details": {
            "audio_tokens": None,
            "cached_tokens": 2600,
            "text_tokens": None,
            "image_tokens": None,
        },
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 2600,
    }
    litellm_usage = Usage(**usage_data)
    usage_record = convert_litellm_usage_to_usage_record(litellm_usage, model="anthropic/claude-3-5-sonnet-20240620")
    print(usage_record)
    assert usage_record.output_tokens_total == 115
    assert usage_record.input_tokens_total == 2629
    assert usage_record.input_cached_tokens == 2600
    assert usage_record.tokens_total == 115 + 2629

    assert usage_record.is_valid, f"Usage inconsistencies detected: {usage_record.inconsistencies}"


def test_openai_cache_usage():
    first = {
        "completion_tokens": 64,
        "prompt_tokens": 2072,
        "total_tokens": 2136,
        "completion_tokens_details": {
            "accepted_prediction_tokens": 0,
            "audio_tokens": 0,
            "reasoning_tokens": 0,
            "rejected_prediction_tokens": 0,
        },
        "prompt_tokens_details": {"audio_tokens": 0, "cached_tokens": 0, "text_tokens": None, "image_tokens": None},
    }
    second = {
        "completion_tokens": 35,
        "prompt_tokens": 2087,
        "total_tokens": 2122,
        "completion_tokens_details": {
            "accepted_prediction_tokens": 0,
            "audio_tokens": 0,
            "reasoning_tokens": 0,
            "rejected_prediction_tokens": 0,
        },
        "prompt_tokens_details": {"audio_tokens": 0, "cached_tokens": 2048, "text_tokens": None, "image_tokens": None},
    }
    first_litellm_usage = Usage(**first)
    second_litellm_usage = Usage(**second)
    first_usage_record = convert_litellm_usage_to_usage_record(first_litellm_usage, model="openai/gpt-4o-mini")
    second_usage_record = convert_litellm_usage_to_usage_record(second_litellm_usage, model="openai/gpt-4o-mini")

    assert first_usage_record.is_valid, f"Usage inconsistencies detected: {first_usage_record.inconsistencies}"
    assert second_usage_record.is_valid, f"Usage inconsistencies detected: {second_usage_record.inconsistencies}"
