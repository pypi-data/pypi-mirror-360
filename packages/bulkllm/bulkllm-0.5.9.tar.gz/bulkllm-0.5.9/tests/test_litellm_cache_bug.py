from collections import defaultdict

import litellm
from litellm.caching.caching import Cache

from bulkllm.llm import initialize_litellm
from bulkllm.llm_configs import model_resolver


def test_litellm_cache_bug(monkeypatch):
    """there was a bug in litellm where the cache key was not being hashed correctly and was not sufficinetly unique"""
    initialize_litellm()

    monkeypatch.setattr(Cache, "_get_hashed_cache_key", lambda k: k)
    key_counts = defaultdict(int)

    for llm_config in model_resolver(["all"]):
        key = litellm.cache.get_cache_key(**llm_config.completion_kwargs())
        key_counts[key] += 1

    for key, count in key_counts.items():
        assert count == 1, f"Key {key} has count {count}"


if __name__ == "__main__":
    test_litellm_cache_bug()
