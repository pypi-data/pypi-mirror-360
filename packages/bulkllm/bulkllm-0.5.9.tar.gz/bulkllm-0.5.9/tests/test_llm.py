import pytest


@pytest.mark.skip
def test_helloworld():
    from bulkllm.llm import completion

    response = completion(model="openai/gpt-4.1-mini", messages=[{"role": "user", "content": "Hello, world!"}])
    print(response)
