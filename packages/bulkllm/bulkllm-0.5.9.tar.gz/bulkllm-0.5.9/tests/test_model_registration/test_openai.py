from bulkllm.model_registration.openai import get_openai_aliases


def test_gpt35_turbo_16k_alias_present():
    aliases = get_openai_aliases()
    assert "openai/gpt-3.5-turbo-16k" in aliases
