from types import SimpleNamespace
from typing import Any, cast

import pytest

from bulkllm.usage_tracker import (
    GLOBAL_TRACKER,
    UsageTracker,
    convert_litellm_usage_to_usage_record,
    track_usage,
)


class Dummy(SimpleNamespace):
    pass


@pytest.fixture(autouse=True)
def _clear_global_tracker() -> None:
    GLOBAL_TRACKER._aggregates.clear()


def test_convert_usage_no_details():
    usage = Dummy(prompt_tokens=5, completion_tokens=7, total_tokens=12)
    rec = convert_litellm_usage_to_usage_record(cast("dict[str, Any]", usage), model="m")
    assert rec.input_text_tokens == 5
    assert rec.output_text_tokens == 7
    assert rec.tokens_total == 12


def test_convert_usage_with_details():
    prompt_details = Dummy(text_tokens=3, image_tokens=2, audio_tokens=None, cached_tokens=None)
    completion_details = Dummy(
        text_tokens=6, audio_tokens=1, reasoning_tokens=0, accepted_prediction_tokens=0, rejected_prediction_tokens=0
    )
    usage = Dummy(
        prompt_tokens=5,
        completion_tokens=7,
        total_tokens=12,
        prompt_tokens_details=prompt_details,
        completion_tokens_details=completion_details,
    )
    rec = convert_litellm_usage_to_usage_record(cast("dict[str, Any]", usage), model="m")
    assert rec.input_image_tokens == 2
    assert rec.output_audio_tokens == 1
    assert rec.tokens_total == 12


def test_usage_tracker_aggregate():
    tracker = UsageTracker("t")
    with tracker:
        track_usage(
            "m",
            input_text_tokens=1,
            input_tokens_total=1,
            output_text_tokens=2,
            output_tokens_total=2,
            tokens_total=3,
            cost_usd=0.1,
        )
    stats = tracker.aggregate_stats()["m"]
    assert stats.request_count.total == 1
    assert stats.stats["input_text_tokens"].total == 1
    assert stats.stats["output_text_tokens"].total == 2
    assert stats.stats["tokens_total"].total == 3


def test_usage_tracker_snapshot() -> None:
    tracker = UsageTracker("snap")
    with tracker:
        track_usage(
            "a",
            input_text_tokens=1,
            input_tokens_total=1,
            output_text_tokens=2,
            output_tokens_total=2,
            tokens_total=3,
        )
        track_usage(
            "a",
            input_text_tokens=3,
            input_tokens_total=3,
            output_text_tokens=4,
            output_tokens_total=4,
            tokens_total=7,
        )
        track_usage(
            "b",
            input_text_tokens=5,
            input_tokens_total=5,
            output_text_tokens=6,
            output_tokens_total=6,
            tokens_total=11,
        )
    snap = tracker.snapshot()
    assert snap["a"]["request_count"]["total"] == 2
    assert snap["a"]["input_text_tokens"]["total"] == 4
    assert snap["a"]["output_text_tokens"]["total"] == 6
    assert snap["a"]["tokens_total"]["total"] == 10
    assert snap["b"]["request_count"]["total"] == 1
    assert snap["b"]["input_text_tokens"]["total"] == 5
    assert snap["b"]["output_text_tokens"]["total"] == 6
    assert snap["b"]["tokens_total"]["total"] == 11
