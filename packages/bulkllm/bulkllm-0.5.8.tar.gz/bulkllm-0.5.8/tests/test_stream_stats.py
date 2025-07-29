import random

import pytest

from bulkllm.stream_stats import UsageStat


def test_usage_stat_basic_stats():
    s = UsageStat()
    for val in [1, 2, 3]:
        s.add(val)

    assert s.count == 3
    assert s.total == 6
    assert s.min == 1
    assert s.max == 3
    assert s.mean == pytest.approx(2.0)


def test_usage_stat_negative_value():
    s = UsageStat()
    with pytest.raises(ValueError, match="Negative values not allowed"):
        s.add(-1)


def test_usage_stat_discrete_lock(monkeypatch):
    s = UsageStat()
    s.add(1)
    assert s.is_discrete is True
    with pytest.raises(TypeError, match="initialised for integers"):
        s.add(1.5)


def test_usage_stat_histogram_discrete():
    s = UsageStat(reservoir_k=100)
    for val in [1] * 5 + [2] * 2 + [3] * 3:
        s.add(val)

    assert s.histogram == [(1, 2, 5), (2, 3, 2), (3, 4, 3)]


def test_usage_stat_histogram_continuous():
    s = UsageStat(reservoir_k=100)
    for val in [0.5, 1.5, 2.5, 3.5]:
        s.add(val)

    hist = s.histogram
    assert len(hist) == 3
    assert hist[0] == (0.5, 1.5, 1)
    assert hist[1] == (1.5, 2.5, 1)
    assert hist[2] == (2.5, 3.5, 2)


def test_usage_stat_percentiles():
    s = UsageStat(reservoir_k=100)
    for val in [1, 3, 5, 7, 9]:
        s.add(val)

    assert s._sorted_sample() == [1, 3, 5, 7, 9]
    assert s.p1 == pytest.approx(1.0)
    assert s.p50 == pytest.approx(5.0)
    assert s.p99 == pytest.approx(9.0)


def test_reservoir_sampling(monkeypatch):
    s = UsageStat(reservoir_k=2)
    s.add(1)
    s.add(2)

    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    s.add(3)
    s.add(4)

    assert s.reservoir_count == 2
    assert set(s.reservoir.keys()) == {3, 4}
