from bulkllm.model_registration.anthropic import convert_anthropic_to_litellm
from bulkllm.model_registration.gemini import convert_gemini_to_litellm
from bulkllm.model_registration.mistral import convert_mistral_to_litellm
from bulkllm.model_registration.openai import convert_openai_to_litellm


def test_convert_openai():
    sample = {
        "id": "gpt-4o",
        "object": "model",
        "owned_by": "openai",
        "root": "gpt-4o",
    }
    result = convert_openai_to_litellm(sample)
    assert result == {
        "model_name": "openai/gpt-4o",
        "model_info": {
            "litellm_provider": "openai",
            "mode": "chat",
            "object": "model",
            "owned_by": "openai",
            "root": "gpt-4o",
        },
    }


def test_convert_openai_tts():
    sample = {
        "id": "tts-1",
        "object": "model",
        "owned_by": "openai",
        "root": "tts-1",
    }
    result = convert_openai_to_litellm(sample)
    assert result == {
        "model_name": "openai/tts-1",
        "model_info": {
            "litellm_provider": "openai",
            "mode": "audio_speech",
            "object": "model",
            "owned_by": "openai",
            "root": "tts-1",
        },
    }


def test_convert_anthropic():
    sample = {
        "id": "claude-3-7-sonnet-20250219",
        "context_window": 1000,
        "deprecation_date": "2026-02-01",
    }
    result = convert_anthropic_to_litellm(sample)
    assert result == {
        "model_name": "anthropic/claude-3-7-sonnet-20250219",
        "model_info": {
            "litellm_provider": "anthropic",
            "mode": "chat",
            "max_input_tokens": 1000,
            "deprecation_date": "2026-02-01",
        },
    }


def test_convert_gemini():
    sample = {
        "name": "models/gemini-2.5-pro-exp-03-25",
        "inputTokenLimit": 2048,
        "outputTokenLimit": 4096,
        "supported_generation_methods": ["generateContent", "countTokens"],
    }
    result = convert_gemini_to_litellm(sample)
    assert result == {
        "model_name": "gemini/gemini-2.5-pro-exp-03-25",
        "model_info": {
            "litellm_provider": "gemini",
            "mode": "chat",
            "max_input_tokens": 2048,
            "max_output_tokens": 4096,
            "supports_prompt_caching": True,
        },
    }


def test_convert_gemini_camel_case():
    sample = {
        "name": "models/gemini-2.5-pro-exp-03-25",
        "inputTokenLimit": 2048,
        "outputTokenLimit": 4096,
        "supportedGenerationMethods": ["generateContent", "countTokens"],
    }
    result = convert_gemini_to_litellm(sample)
    assert result == {
        "model_name": "gemini/gemini-2.5-pro-exp-03-25",
        "model_info": {
            "litellm_provider": "gemini",
            "mode": "chat",
            "max_input_tokens": 2048,
            "max_output_tokens": 4096,
            "supports_prompt_caching": True,
        },
    }


def test_convert_gemini_adds_version():
    sample = {
        "name": "models/gemini-2.5-pro-exp-03-25",
        "version": "2.5-exp-03-25",
    }
    result = convert_gemini_to_litellm(sample)
    assert result == {
        "model_name": "gemini/gemini-2.5-pro-exp-03-25",
        "model_info": {
            "litellm_provider": "gemini",
            "mode": "chat",
            "version": "2.5-exp-03-25",
        },
    }


def test_convert_mistral():
    sample = {
        "id": "mistral-small",
        "max_context_length": 8192,
        "capabilities": {"function_calling": True, "vision": True},
    }
    result = convert_mistral_to_litellm(sample)
    assert result == {
        "model_name": "mistral/mistral-small",
        "model_info": {
            "litellm_provider": "mistral",
            "mode": "chat",
            "max_input_tokens": 8192,
            "supports_function_calling": True,
            "supports_vision": True,
        },
    }


def test_keyword_mode_openai_embed():
    result = convert_openai_to_litellm({"id": "text-embed-foo"})
    assert result["model_info"]["mode"] == "embedding"


def test_keyword_mode_anthropic_moderation():
    result = convert_anthropic_to_litellm({"id": "guard-moderation"})
    assert result["model_info"]["mode"] == "moderation"


def test_keyword_mode_mistral_ocr():
    result = convert_mistral_to_litellm({"id": "mistral-ocr-123"})
    assert result["model_info"]["mode"] == "ocr"
