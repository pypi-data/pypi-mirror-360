"""cost_tracker.py — comprehensive usage & cost tracking
---------------------------------------------------
Tracks fine-grained token usage, latency, and cost for LLM calls in an
async-safe manner.  Designed around litellm`s `Usage` schema but can be
fed manual tallies as well.

Public API
~~~~~~~~~~
* ``track_usage(...)`` - primary recording entry-point.
  ``track_usage`` for backward compatibility.
* ``UsageTracker`` - async (and sync) context manager accumulating
  per-model aggregates.  A module-level ``GLOBAL_TRACKER`` is always
  active.

The module intentionally omits any thread-safety primitives, export, or
reporting utilities.
"""

from __future__ import annotations

import contextvars
import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

from bulkllm.stream_stats import UsageStat

logger = logging.getLogger(__name__)


class UsageRecord(BaseModel):
    """Single request accounting entry (flat)."""

    # ---- raw tallies (prompt / input) ----
    input_text_tokens: int = 0
    input_image_tokens: int = 0
    input_audio_tokens: int = 0
    input_cached_tokens: int = 0
    input_tokens_total: int = 0

    # ---- raw tallies (completion / output) ----
    output_text_tokens: int = 0
    output_image_tokens: int = 0
    output_audio_tokens: int = 0
    output_reasoning_tokens: int = 0
    output_accepted_prediction_tokens: int = 0
    output_rejected_prediction_tokens: int = 0
    output_tokens_total: int = 0

    # ---- derived aggregate ----
    tokens_total: int = 0

    # ---- timing & cost ----
    time_ms: float | None = None
    cost_usd: float | None = None

    # ---- metadata ----
    model: str
    is_cached_hit: bool = False
    ts_completed: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # ---- validation extras ----
    is_valid: bool = True
    inconsistencies: list[str] = Field(default_factory=list, repr=False)

    @model_serializer(mode="wrap")
    def _strip_null_and_zero(self, handler):
        """Omit ``None`` and zero values when serialising."""
        original: dict = handler(self)  # let Pydantic build the dict
        filtered: dict = {}

        for k, v in original.items():
            if v is None:
                continue
            if isinstance(v, int | float) and v == 0:
                continue
            # Round time_ms to 3 decimal places
            if k == "time_ms" and v is not None:
                filtered[k] = round(v, 3)
            else:
                filtered[k] = v
        return filtered

    @model_validator(mode="after")
    def _validate_totals(self) -> UsageRecord:
        """Ensure all derived totals match their component sums."""
        errors: list[str] = []

        # Helper for consistency checks
        def _check(sum_components: int, expected: int, label: str) -> None:
            """Append a formatted error if totals don't match."""
            if expected == 0:
                return  # provider omitted detailed breakdown
            if sum_components != expected:
                errors.append(f"{label}: expected {expected}, computed {sum_components}")

        _check(
            self.input_text_tokens + self.input_image_tokens + self.input_audio_tokens + self.input_cached_tokens,
            self.input_tokens_total,
            "input total mismatch",
        )
        _check(
            self.output_text_tokens
            + self.output_audio_tokens
            + self.output_reasoning_tokens
            + self.output_accepted_prediction_tokens
            + self.output_rejected_prediction_tokens,
            self.output_tokens_total,
            "output total mismatch",
        )
        _check(
            self.input_tokens_total + self.output_tokens_total,
            self.tokens_total,
            "grand total mismatch",
        )

        self.is_valid = not errors

        if errors:
            errors = list(set(errors))
            self.inconsistencies.extend(errors)
            self.inconsistencies = list(set(self.inconsistencies))
            logger.debug(
                "UsageRecord inconsistencies detected for model '%s': %s",
                self.model,
                "; ".join(errors),
            )

        return self


# ---------------------------------------------------------------------------
# Aggregation containers
# ---------------------------------------------------------------------------


class UsageAggregate(BaseModel):
    """
    Rolling aggregate keyed exactly to fields in `UsageRecord`
    plus two meta counters (`request_count`, `invalid_count`).

    Any new numeric field you add to UsageRecord is
    automatically aggregated without code changes.
    """

    model: str

    # meta counters ----------------------------------------------------
    request_count: UsageStat = Field(default_factory=UsageStat)
    invalid_count: UsageStat = Field(default_factory=UsageStat)

    # one bucket per numeric UsageRecord field ------------------------
    stats: dict[str, UsageStat] = Field(default_factory=lambda: defaultdict(UsageStat))

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    # -----------------------------------------------------------------
    def add(self, rec: UsageRecord | list[UsageRecord]) -> None:  # ← single source of truth
        """Incorporate a new usage record into the aggregates."""
        if isinstance(rec, UsageRecord):
            rec = [rec]

        for r in rec:
            self.request_count.add(1)
            if not r.is_valid:
                self.invalid_count.add(1)

            for field_name, value in r.__dict__.items():
                if isinstance(value, int | float | bool) and field_name != "model":
                    self.stats[field_name].add(value)

    # -----------------------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serialisable snapshot of the aggregates."""
        dump = {
            "model": self.model,
            "request_count": self.request_count.model_dump(mode="json"),
            "invalid_count": self.invalid_count.model_dump(mode="json"),
        }
        dump.update({k: v.model_dump(mode="json") for k, v in self.stats.items()})
        return dump


# ---------------------------------------------------------------------------
# UsageTracker - async/sync context manager
# ---------------------------------------------------------------------------


class UsageTracker:
    """Async-safe accumulator shared via a contextvar stack."""

    __slots__ = ("_aggregates", "_token", "name")

    def __init__(self, name: str | None = None) -> None:
        """Initialise an empty tracker with an optional name."""
        self.name = name or "Unnamed"
        self._aggregates: dict[str, UsageAggregate] = {}
        self._token: contextvars.Token | None = None

    # ------------------------------------------------------------- context mgr
    async def __aenter__(self) -> UsageTracker:
        """Enter the tracker context asynchronously."""
        return self._enter()

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        """Exit the async context."""
        self._exit()

    def __enter__(self) -> UsageTracker:  # type: ignore[override]
        """Enter the tracker context."""
        return self._enter()

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        """Exit the tracker context."""
        self._exit()

    def _enter(self) -> UsageTracker:
        """Push this tracker onto the context variable stack."""
        current = _usage_stack_var.get()
        self._token = _usage_stack_var.set((*current, self))
        return self

    def _exit(self) -> None:
        """Pop this tracker from the context variable stack."""
        if self._token is not None:
            _usage_stack_var.reset(self._token)
            self._token = None

    # ------------------------------------------------------------- internals
    def _add_record(self, record: UsageRecord) -> None:
        """Internal helper to add a record to the correct aggregate."""
        agg = self._aggregates.setdefault(record.model, UsageAggregate(model=record.model))
        agg.add(record)

    # ------------------------------------------------------------- public API
    def snapshot(self) -> dict[str, Any]:
        """Deep-copy view for diagnostics."""
        return {m: agg.snapshot() for m, agg in self._aggregates.items()}

    def aggregate_stats(self) -> dict[str, UsageAggregate]:
        """Return access to the internal aggregates mapping."""
        return self._aggregates


# ---------------------------------------------------------------------------
# Global tracker & contextvar stack initialisation
# ---------------------------------------------------------------------------

GLOBAL_TRACKER = UsageTracker("global")
_usage_stack_var: contextvars.ContextVar[tuple[UsageTracker, ...]] = contextvars.ContextVar("_usage_stack_var")
_usage_stack_var.set((GLOBAL_TRACKER,))


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------
def convert_litellm_usage_to_usage_record(
    litellm_usage: dict[str, Any],
    model: str,
    *,
    time_ms: float | None = None,
    cost_usd: float | None = None,
    is_cached_hit: bool = False,
) -> UsageRecord:
    """Translate ``litellm.Usage`` into ``UsageRecord``.

    Assumptions
    -----------
    • If *no* details object is present, **all** tokens are considered *text*
    • If a details object *is* present but every token-field is zero / ``None``,
      we also treat the total as *text* tokens.
    """

    # ---------- prompt tokens ----------------------------------------
    pt_details = getattr(litellm_usage, "prompt_tokens_details", None)

    itext = getattr(pt_details, "text_tokens", None) or 0
    iimg = getattr(pt_details, "image_tokens", None) or 0
    iaud = getattr(pt_details, "audio_tokens", None) or 0
    icache = getattr(pt_details, "cached_tokens", None) or 0

    # If details are missing **or** entirely empty, assume everything is text
    if (pt_details is None) or (itext + iimg + iaud + icache == 0):
        itext = getattr(litellm_usage, "prompt_tokens", 0) or (
            itext + iimg + iaud + icache  # fall back to 0
        )
        iimg = iaud = icache = 0

    # authoritative total if supplied
    input_total = getattr(litellm_usage, "prompt_tokens", None)
    if input_total is None:
        input_total = itext + iimg + iaud + icache

    # ---------- completion tokens ------------------------------------
    ct_details = getattr(litellm_usage, "completion_tokens_details", None)

    otext = getattr(ct_details, "text_tokens", None) or 0
    if "xai/grok-3-mini-beta" in model and otext == 0:
        otext = getattr(litellm_usage, "completion_tokens", 0)
    oaud = getattr(ct_details, "audio_tokens", None) or 0
    oreason = getattr(ct_details, "reasoning_tokens", None) or 0
    oacc = getattr(ct_details, "accepted_prediction_tokens", None) or 0
    orej = getattr(ct_details, "rejected_prediction_tokens", None) or 0

    # Same assumption logic for outputs
    if (ct_details is None) or (otext + oaud + oreason + oacc + orej == 0):
        otext = getattr(litellm_usage, "completion_tokens", 0) or (otext + oaud + oreason + oacc + orej)
        oaud = oreason = oacc = orej = 0

    logged_output_total = getattr(litellm_usage, "completion_tokens", None)

    computed_output_total = otext + oaud + oreason + oacc + orej
    output_total = logged_output_total if logged_output_total is not None else computed_output_total

    if logged_output_total is not None and logged_output_total != computed_output_total:  # noqa
        if logged_output_total > computed_output_total and otext == 0:
            otext = logged_output_total - computed_output_total

    if (
        "xai/grok-3-mini-beta" in model
        and logged_output_total is not None
        and computed_output_total > logged_output_total
    ):
        output_total = computed_output_total

    # ---------- grand total ------------------------------------------
    grand_total = getattr(litellm_usage, "total_tokens", None)
    if grand_total is None:
        grand_total = input_total + output_total

    # ---------- UsageRecord ------------------------------------------
    return UsageRecord(
        model=model,
        # input breakdown
        input_text_tokens=itext,
        input_image_tokens=iimg,
        input_audio_tokens=iaud,
        input_cached_tokens=icache,
        input_tokens_total=input_total,
        # output breakdown
        output_text_tokens=otext,
        output_audio_tokens=oaud,
        output_reasoning_tokens=oreason,
        output_accepted_prediction_tokens=oacc,
        output_rejected_prediction_tokens=orej,
        output_tokens_total=output_total,
        # aggregate
        tokens_total=grand_total,
        # timing & cost
        time_ms=time_ms,
        cost_usd=cost_usd,
        is_cached_hit=is_cached_hit,
    )


# ---------------------------------------------------------------------------
# track_usage - public entry-point
# ---------------------------------------------------------------------------


def track_usage(
    model: str,
    *,
    record: UsageRecord | None = None,
    litellm_usage: dict[str, Any] | None = None,
    # direct counts ----------------------------------------------------
    input_text_tokens: int = 0,
    input_image_tokens: int = 0,
    input_audio_tokens: int = 0,
    input_cached_tokens: int = 0,
    input_tokens_total: int = 0,
    output_text_tokens: int = 0,
    output_audio_tokens: int = 0,
    output_reasoning_tokens: int = 0,
    output_accepted_prediction_tokens: int = 0,
    output_rejected_prediction_tokens: int = 0,
    output_tokens_total: int = 0,
    tokens_total: int = 0,
    # timing & cost ----------------------------------------------------
    time_ms: float | None = None,
    cost_usd: float | None = None,
    is_cached_hit: bool = False,
) -> None:
    """Record a single request`s accounting information.

    Exactly **one** of the following should be provided:
    * ``record``  - pre-constructed ``UsageRecord``
    * ``litellm_usage`` - raw litellm ``Usage``
    * individual keyword tallies (default path)
    """

    # ------------------------------------------------------------------ construct UsageRecord
    if record is not None:
        _rec = record
    elif litellm_usage is not None:
        _rec = convert_litellm_usage_to_usage_record(litellm_usage, model, time_ms=time_ms, cost_usd=cost_usd)
    else:
        _rec = UsageRecord(
            model=model,
            input_text_tokens=input_text_tokens,
            input_image_tokens=input_image_tokens,
            input_audio_tokens=input_audio_tokens,
            input_cached_tokens=input_cached_tokens,
            input_tokens_total=input_tokens_total,
            output_text_tokens=output_text_tokens,
            output_audio_tokens=output_audio_tokens,
            output_reasoning_tokens=output_reasoning_tokens,
            output_accepted_prediction_tokens=output_accepted_prediction_tokens,
            output_rejected_prediction_tokens=output_rejected_prediction_tokens,
            output_tokens_total=output_tokens_total,
            tokens_total=tokens_total,
            time_ms=time_ms,
            cost_usd=cost_usd,
            is_cached_hit=is_cached_hit,
        )

    # ------------------------------------------------------------------ push to all active trackers
    for tracker in _usage_stack_var.get():
        tracker._add_record(_rec)
