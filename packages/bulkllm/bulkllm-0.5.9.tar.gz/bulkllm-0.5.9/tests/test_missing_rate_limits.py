from bulkllm.llm_configs import model_resolver


def test_model_resolver_no_missing_rate_limits():
    """Fail if any configured model is missing a rate-limit entry.

    The ``missing-rate-limits`` group expands to all models that do not have a
    corresponding entry in ``bulkllm.rate_limits.DEFAULT_RATE_LIMITS``.  A
    non-empty result indicates that new models were added without an explicit
    rate-limit configuration and CI must fail so the limits can be updated.
    """
    missing = model_resolver(["missing-rate-limits"])

    # If *missing* is truthy the assertion will fail and clearly list the
    # offending model slugs.
    assert not missing, "Models missing rate limits: " + ", ".join(cfg.slug for cfg in missing)
