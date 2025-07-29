import math
import random

from pydantic import BaseModel, ConfigDict, Field, computed_field

RESERVOIR_K = 10_000


class UsageStat(BaseModel):
    """
    Metric accumulator with streaming stats and a fixed-size reservoir that
    stores a *frequency table* (value → multiplicity).  The class now:

    • Detects whether the series is *discrete* (int) or *continuous* (float)
      on the first `add()` and locks that decision (`is_discrete`).
    • Builds histograms with a data-driven number of buckets:
        - Discrete: one bucket per integer up to `max_bins` (default 20).
        - Continuous: Freedman-Diaconis / Sturges / √n heuristic, capped at
          `max_bins`.
    """

    # running tallies -------------------------------------------------
    count: int = 0
    total: int | float = 0
    min: int | float | None = None
    max: int | float | None = None

    # reservoir -------------------------------------------------------
    reservoir: dict[int | float, int] | None = None  # value → multiplicity
    reservoir_count: int = Field(0, exclude=True)
    reservoir_k: int = Field(default=RESERVOIR_K, exclude=False)

    # new - data-kind lock-in ----------------------------------------
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
            self.is_discrete = isinstance(value, int)
        elif self.is_discrete and not isinstance(value, int):
            msg = "UsageStat initialised for integers, but received a non-integer value"
            raise TypeError(msg)

        # update aggregates ------------------------------------------
        self.count += 1
        self.total += value
        self.min = value if self.min is None else min(self.min, value)
        self.max = value if self.max is None else max(self.max, value)

        # initialise reservoir lazily --------------------------------
        if self.reservoir is None:
            self.reservoir = {}

        # ----------- Vitter`s Algorithm R with freq table ------------
        if self.reservoir_count < self.reservoir_k:
            self.reservoir[value] = self.reservoir.get(value, 0) + 1
            self.reservoir_count += 1
        else:
            j = random.randint(0, self.count - 1)
            if j < self.reservoir_k:
                # remove a random element (probability 1/k)
                idx = random.randint(0, self.reservoir_count - 1)
                running = 0
                for v, c in list(self.reservoir.items()):
                    running += c
                    if idx < running:
                        self.reservoir[v] = c - 1 if c > 1 else 0
                        if self.reservoir[v] == 0:
                            del self.reservoir[v]
                        break
                # insert the new value
                self.reservoir[value] = self.reservoir.get(value, 0) + 1
                # reservoir_count stays constant (k)

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
        """Return the percentile of *data* using linear interpolation."""
        if not data:
            return 0.0
        idx = round(pct * (len(data) - 1))
        return float(data[idx])

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
