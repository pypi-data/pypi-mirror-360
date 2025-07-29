import datetime

from bulkllm.schema import LLMConfig

LLMConfig.model_rebuild(_types_namespace={"datetime": datetime})


def test_llmconfig_md5_and_kwargs():
    cfg1 = LLMConfig(
        slug="s1",
        display_name="S1",
        company_name="ACME",
        litellm_model_name="model-1",
        llm_family="s1",
        temperature=0.1,
        max_tokens=100,
        system_prompt="hello",
    )
    cfg2 = cfg1.model_copy(update={"temperature": 0.2})

    assert cfg1.md5_hash != cfg2.md5_hash

    kwargs = cfg1.completion_kwargs()
    assert kwargs["model"] == "model-1"
    assert kwargs["temperature"] == 0.1
    assert kwargs["max_tokens"] == 100
    assert kwargs["stream"] is False
