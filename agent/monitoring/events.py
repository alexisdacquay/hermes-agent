"""Typed gateway monitoring events.

Content-free service-health and redacted diagnostic events for the gateway
daemon — the only shapes the monitoring plane emits: no prompts, messages,
tool args/results, session history, or usage analytics. Field order is wire
order (``asdict``); never reorder.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar


class _MonitoringEvent:
    __slots__ = ()
    EVENT: ClassVar[str]

    def to_dict(self) -> dict[str, Any]:
        return {"event": self.EVENT, **asdict(self)}


@dataclass(slots=True)
class GatewayHealthEvent(_MonitoringEvent):
    """Content-free gateway health snapshot or lifecycle event."""
    EVENT: ClassVar[str] = "gateway_health"
    name: str
    gateway_state: str | None = None
    old_state: str | None = None
    new_state: str | None = None
    exit_reason: str | None = None
    restart_requested: bool | None = None
    active_agents: int = 0
    gateway_busy: bool = False
    gateway_drainable: bool = False
    platform_count: int = 0
    fatal_platform_count: int = 0
    profile: str | None = None
    install_id: str | None = None
    version: str | None = None
    supervision_mode: str | None = None
    pid: int | None = None
    ts_ns: int = field(default_factory=time.time_ns)


@dataclass(slots=True)
class GatewayDiagnosticEvent(_MonitoringEvent):
    """Redacted gateway diagnostic event for operator-owned observability."""
    EVENT: ClassVar[str] = "gateway_diagnostic"
    name: str
    subsystem: str
    error_class: str = "unknown"
    error_code: str | None = None
    platform: str | None = None
    old_state: str | None = None
    new_state: str | None = None
    profile: str | None = None
    version: str | None = None
    severity: str = "warning"
    ts_ns: int = field(default_factory=time.time_ns)
    source_logger: str | None = None


@dataclass(slots=True)
class CronExecutionEvent(_MonitoringEvent):
    """Content-free durable cron execution lifecycle projection."""
    EVENT: ClassVar[str] = "cron_execution"
    status: str
    job_key: str
    source: str = "unknown"
    duration_ms: int | None = None
    delivery_outcome: str | None = None
    error_class: str | None = None
    ts_ns: int = field(default_factory=time.time_ns)


__all__ = ["CronExecutionEvent", "GatewayDiagnosticEvent", "GatewayHealthEvent"]
