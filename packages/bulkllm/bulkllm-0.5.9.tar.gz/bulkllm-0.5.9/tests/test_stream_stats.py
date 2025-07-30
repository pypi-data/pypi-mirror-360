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

    seq = iter([0.1, 0.2, 0.3])
    monkeypatch.setattr(random, "random", lambda: next(seq))
    monkeypatch.setattr(random, "randrange", lambda n: 0)

    s.add(3)
    s.add(4)

    assert sum(s.reservoir.values()) == 2
    assert 4 in s.reservoir


def test_exact_to_sample_switch():
    s = UsageStat(reservoir_k=10_000)
    for i in range(10_001):
        s.add(i)

    assert s.sample_mode is True
    assert sum(s.reservoir.values()) == 10_000
    assert len(s.reservoir) <= 10_000


def test_exact_mode_stable():
    s = UsageStat(reservoir_k=10_000)
    for i in range(500):
        s.add(i)

    assert s.sample_mode is False
    for i in range(500):
        assert s.reservoir[i] == 1
    assert sum(s.reservoir.values()) == 500


def test_mean_min_max_continuity():
    s = UsageStat(reservoir_k=10_000)
    for i in range(10_000):
        s.add(i)

    expected_mean = sum(range(10_000)) / 10_000
    assert s.mean == pytest.approx(expected_mean)
    assert s.min == 0
    assert s.max == 9_999

    s.add(10_000)

    assert s.sample_mode is True
    new_mean = (sum(range(10_000)) + 10_000) / 10_001
    assert s.mean == pytest.approx(new_mean)
    assert s.min == 0
    assert s.max == 10_000
