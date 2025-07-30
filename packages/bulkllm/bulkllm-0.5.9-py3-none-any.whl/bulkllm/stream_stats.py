import heapq
import math
import random
from collections import Counter

from pydantic import BaseModel, ConfigDict, Field, computed_field

RESERVOIR_K = 10_000


class UsageStat(BaseModel):
    """
    Metric accumulator with streaming stats and a cardinality-adaptive reservoir.

    ``reservoir`` begins as an exact frequency table (value → count) and, once
    the number of distinct values exceeds ``reservoir_k``, it automatically
    downgrades to a fixed-size uniform sample where the counts represent the
    number of copies inside the reservoir.

    The class also:

    • Detects whether the series is *discrete* (int) or *continuous* (float)
      on the first `add()` and locks that decision (`is_discrete`).
    • Builds histograms with a data-driven number of buckets:
        - Discrete: one bucket per integer up to `max_bins` (default 20).
        - Continuous: Freedman-Diaconis / Sturges / √n heuristic, capped at
          ``max_bins``.
    """

    round_to: int | None = None

    # running tallies -------------------------------------------------
    count: int = 0
    total: int | float = 0
    min: int | float | None = None
    max: int | float | None = None

    # reservoir -------------------------------------------------------
    reservoir: dict[int | float, int] = Field(default_factory=dict)
    sample_mode: bool = False
    reservoir_k: int = Field(default=RESERVOIR_K, exclude=False)

    # data-kind lock-in ----------------------------------------
    is_discrete: bool | None = Field(default=None, exclude=False)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    # ----------------------------------------------------------------
    # public API
    # ----------------------------------------------------------------
    def add(self, value: int | float | bool | None) -> None:
        """Add a value to the running statistics."""
        if value is None:
            return
        if isinstance(value, bool):
            value = int(value)

        if isinstance(value, int | float) and value < 0:
            msg = "Negative values not allowed for UsageStat"
            raise ValueError(msg)

        # ----- lock in data kind on first insert ---------------------
        if self.is_discrete is None and value > 0:
            self.is_discrete = isinstance(value, int) or self.round_to == 0
        elif self.is_discrete and not isinstance(value, int):
            msg = "UsageStat initialised for integers, but received a non-integer value"
            raise TypeError(msg)

        # ----- round if rounding is configured ------------------
        if self.round_to is not None and isinstance(value, float):
            value = round(value, self.round_to)

        # update aggregates ------------------------------------------
        self.count += 1
        self.total += value
        self.min = value if self.min is None else min(self.min, value)
        self.max = value if self.max is None else max(self.max, value)

        # ----- adaptive reservoir updates ----------------------------
        if not self.sample_mode:
            self.reservoir[value] = self.reservoir.get(value, 0) + 1
            if len(self.reservoir) > self.reservoir_k:
                self._convert_to_sample_mode()
        else:
            self._reservoir_update_sample_mode(value)

        self._assert_invariants()

    # ----------------------------------------------------------------
    # helpers for percentile / histogram
    # ----------------------------------------------------------------
    def _sorted_sample(self) -> list[int | float]:
        """Return the reservoir as a sorted list of values."""
        if not self.reservoir:
            return []
        sample: list[int | float] = []
        for v, c in self.reservoir.items():
            sample.extend([v] * c)
        return sorted(sample)

    def _percentile(self, pct: float, data: list[int | float]) -> float:
        """Return the percentile of *data*"""
        if not data:
            return 0.0
        idx = round(pct * (len(data) - 1))
        return float(data[idx])

    # ------------------------------------------------------------------
    # reservoir helpers
    # ------------------------------------------------------------------
    def _convert_to_sample_mode(self) -> None:
        """Convert exact counts to a uniform reservoir sample."""
        key_weight_pairs = [(random.random() ** (1 / c), v) for v, c in self.reservoir.items()]
        top = heapq.nlargest(self.reservoir_k, key_weight_pairs)
        self.reservoir = Counter(v for _, v in top)
        self.sample_mode = True

    def _reservoir_update_sample_mode(self, x: int | float) -> None:
        j = random.randrange(self.count)
        if j < self.reservoir_k:
            idx = random.randrange(self.reservoir_k)
            running = 0
            for v, c in list(self.reservoir.items()):
                if running + c > idx:
                    self.reservoir[v] = c - 1
                    if self.reservoir[v] == 0:
                        del self.reservoir[v]
                    break
                running += c
            self.reservoir[x] = self.reservoir.get(x, 0) + 1

    def _assert_invariants(self) -> None:
        if len(self.reservoir) > self.reservoir_k:
            raise ValueError("reservoir cardinality invariant violated")
        if self.sample_mode and self.count < self.reservoir_k + 1:
            raise ValueError("sample mode before reservoir full")

    # ---------- adaptive bin rules for continuous data --------------
    def _auto_bins(self, data: list[float], max_bins: int) -> int:
        """Choose a bin count based on data size and spread."""
        n = len(data)
        if n < 2:
            return 1
        if n < 30:
            return max(1, min(max_bins, math.ceil(1 + math.log2(n))))  # Sturges

        # IQR-based Freedman-Diaconis
        q1_idx = int(0.25 * (n - 1))
        q3_idx = int(0.75 * (n - 1))
        iqr = data[q3_idx] - data[q1_idx]
        if iqr == 0:
            return max(1, min(max_bins, math.ceil(math.sqrt(n))))  # √n fallback

        bin_width = 2 * iqr / (n ** (1 / 3))
        if bin_width == 0:
            return 1
        bin_count = math.ceil((self.max - self.min) / bin_width)
        return max(1, min(max_bins, bin_count))

    # ---------- unified histogram construction ----------------------
    def _histogram(self, max_bins: int, data: list[int | float]) -> list[tuple[int | float, int | float, int]]:
        """Build a histogram from *data* with at most *max_bins* buckets."""
        if not data or self.min is None or self.max is None or max_bins <= 0:
            return []

        if self.max == self.min:
            return [(self.min, self.max, len(data))]

        # ── DISCRETE SERIES ───────────────────────────────────────────────
        if self.is_discrete:
            ideal_bins = int(self.max - self.min) + 1  # one per int
            bin_count = max(1, min(ideal_bins, max_bins))
            width = math.ceil(ideal_bins / bin_count)

            buckets = [
                [
                    int(self.min + i * width),  # lower (inclusive)
                    int(self.min + (i + 1) * width),  # upper (exclusive)
                    0,
                ]  # count
                for i in range(bin_count)
            ]

            for v in data:
                idx = min((v - self.min) // width, bin_count - 1)
                buckets[idx][2] += 1

        # ── CONTINUOUS SERIES ─────────────────────────────────────────────
        else:
            bin_count = self._auto_bins(data, max_bins)
            width = (self.max - self.min) / bin_count
            buckets = [
                [
                    self.min + i * width,  # lower (inclusive)
                    self.min + (i + 1) * width if i < bin_count - 1 else self.max,
                    0,
                ]
                for i in range(bin_count)
            ]
            for v in data:
                idx = min(int((v - self.min) / width), bin_count - 1)
                buckets[idx][2] += 1

        # Cast to tuple so the snapshot is immutable
        return [tuple(b) for b in buckets]

    # ------------------------------------------------------------------
    # computed distribution-aware metrics
    # ------------------------------------------------------------------
    @computed_field(return_type=float)
    def mean(self) -> float:
        """Return the arithmetic mean of all values seen."""
        return self.total / self.count if self.count else 0.0

    @computed_field(return_type=float)
    def p1(self) -> float:
        """Return the 1st percentile of the sample."""
        return self._percentile(0.01, self._sorted_sample())

    @computed_field(return_type=float)
    def p5(self) -> float:
        """Return the 5th percentile of the sample."""
        return self._percentile(0.05, self._sorted_sample())

    @computed_field(return_type=float)
    def p50(self) -> float:
        """Return the median of the sample."""
        return self._percentile(0.50, self._sorted_sample())

    @computed_field(return_type=float)
    def p95(self) -> float:
        """Return the 95th percentile of the sample."""
        return self._percentile(0.95, self._sorted_sample())

    @computed_field(return_type=float)
    def p99(self) -> float:
        """Return the 99th percentile of the sample."""
        return self._percentile(0.99, self._sorted_sample())

    @computed_field(return_type=list[tuple[float, float, int]])
    def histogram(self) -> list[tuple[float, float, int]]:
        """Adaptive histogram (≤ 20 buckets by default)."""
        return self._histogram(20, self._sorted_sample())
