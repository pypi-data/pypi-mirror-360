from bulkllm.model_registration import utils


class DummyError(Exception):
    pass


def test_added_models(monkeypatch, capsys):
    utils.ADDED_MODELS.clear()

    def fake_get_model_info(name: str):
        if name == "exists/model":
            return {"dummy": 1}
        raise DummyError("not found")

    recorded: dict[str, object] = {}

    monkeypatch.setattr(utils.litellm, "get_model_info", fake_get_model_info)
    monkeypatch.setattr(utils.litellm, "register_model", lambda data: recorded.update(data))
    model_info = {
        "max_tokens": 8192,
        "input_cost_per_token": 0.00002,
        "output_cost_per_token": 0.00006,
        "litellm_provider": "openai",
        "mode": "chat",
    }

    utils.bulkllm_register_models({"exists/model": model_info, "new/model": model_info}, source="testsrc")

    assert ("new/model", "testsrc") in utils.ADDED_MODELS
    assert ("exists/model", "testsrc") not in utils.ADDED_MODELS

    utils.print_added_models()
    out = capsys.readouterr().out
    assert "new/model - testsrc" in out
