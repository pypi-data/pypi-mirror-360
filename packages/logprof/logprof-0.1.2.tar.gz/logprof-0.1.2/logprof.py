import logging
from contextlib import ContextDecorator
from time import perf_counter_ns

# some platforms don't have resource (e.g. WASI)
try:
    import resource
except ImportError:
    resource = None  # type: ignore


def _format_time(rem_ns, format) -> str:
    if format == "seconds":
        return f"{rem_ns / 10**9:.3f}s"
    elif format == "breakdown":
        dpc_m, rem_ns = divmod(rem_ns, 60 * 10**9)
        dpc_s, rem_ns = divmod(rem_ns, 10**9)
        dpc_ms, rem_ns = divmod(rem_ns, 10**6)
        dpc_us, rem_ns = divmod(rem_ns, 10**3)
        parts: list[str] = []
        for v, unit in zip(
            (dpc_m, dpc_s, dpc_ms, dpc_us, rem_ns), ("m", "s", "ms", "us", "ns")
        ):
            if v != 0 or len(parts):
                parts.append(f"{v}{unit}")
        return " ".join(parts)
    elif format == "nanoseconds":
        return f"{rem_ns}ns"
    # TODO: support callable or format string
    return f"{rem_ns}ns"


def _format_memory(rem_kb, format) -> str:
    if format == "human":
        rem_b = rem_kb * 1024
        for unit in ("", "kib", "mib", "gib"):
            if abs(rem_b) < 1024.0:
                return f"{rem_b:3.1f}{unit}"
            rem_b /= 1024.0
        return f"{rem_b:.1f}tib"
    elif format == "breakdown":
        drss_gb, rem_kb = divmod(rem_kb, 1024**2)
        drss_mb, rem_kb = divmod(rem_kb, 1024**1)
        parts: list[str] = []
        for v, unit in zip((drss_gb, drss_mb, rem_kb), ("gib", "mib", "kib")):
            if v != 0 or len(parts):
                parts.append(f"{v}{unit}")
        return " ".join(parts)
    elif format == "kilobytes":
        return f"{rem_kb}kib"
    # TODO: support callable or format string
    return f"{rem_kb}kib"


class logprof(ContextDecorator):
    """Log profiling information."""

    def __init__(
        self,
        label: str,
        tf: str | None = "seconds",
        mf: str | None = None,
        logger: logging.Logger | None = None,
        level: str = "INFO",
        **kwds,
    ):
        """Construct a logprof context decorator.

        `label` is displayed before
        and after the decorated function is called. `tf` is a time format and
        can be one of "seconds", "nanoseconds", "breakdown" or None. `mf` is a
        memory format and can be one of "kilobytes", "human", "breakdown" or
        None. If either `tf` or `mf` is None, no time or memory information is
        logged. `logger` is the logger to use. `level` is the log level to use.
        When used as a context manager, the attributes `ns_delta` and `kb_delta`
        are set to the time and memory deltas, respectively.
        """
        if tf not in (None, "seconds", "nanoseconds", "breakdown"):
            raise ValueError(f"Invalid time format: {tf}")
        if mf not in (None, "kilobytes", "human", "breakdown"):
            raise ValueError(f"Invalid memory format: {mf}")
        self.label = label
        self.tf = tf
        self.mf = mf
        self.ns_delta = None
        self.kb_delta = None
        self.logger = logger or logging.getLogger(__name__)
        self.level = (
            level if isinstance(level, int) else logging._nameToLevel[level.upper()]
        )

    def __enter__(self):
        self.logger.log(self.level, f">>> '{self.label}' started..")

        if self.tf is not None:
            self.pcns = perf_counter_ns()

        if resource is not None and self.mf is not None:
            self.ru = resource.getrusage(resource.RUSAGE_SELF)
        return self

    def __exit__(self, *exc):
        parts = [f"<<< '{self.label}' finished."]

        if self.tf is not None:
            self.ns_delta = rem_ns = perf_counter_ns() - self.pcns
            parts.append("Took " + _format_time(rem_ns, self.tf) + ".")

        if resource is not None and self.mf is not None:
            ru = resource.getrusage(resource.RUSAGE_SELF)
            self.kb_delta = rem_kb = ru.ru_maxrss - self.ru.ru_maxrss
            parts.append("Used " + _format_memory(rem_kb, self.mf) + ".")

        self.logger.log(self.level, " ".join(parts))
        return False
