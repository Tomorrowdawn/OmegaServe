"""API-facing controller interfaces.

These classes describe the operational surface of OmegaServe without
committing to a specific web framework.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from omegaconf import DictConfig

from .runtime import Runtime
from .service import Service


class ServiceStatus(enum.Enum):
    """High-level lifecycle status for a managed service."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    RESTARTING = "restarting"
    FAILED = "failed"


@dataclass
class StatusReport:
    status: ServiceStatus
    config: Optional[DictConfig] = None
    message: Optional[str] = None


@dataclass
class RestartRequest:
    config: Optional[DictConfig] = None
    overrides: Sequence[str] = ()


class ServiceController:
    """Lifecycle management contract for services."""

    def __init__(self, service: Service, runtime: Runtime):
        self.service = service
        self.runtime = runtime

    def status(self, include_config: bool = False) -> StatusReport:
        """Return the current service status and optionally its configuration."""

        raise NotImplementedError

    def restart(self, request: RestartRequest) -> StatusReport:
        """Restart the service with the given configuration overrides."""

        raise NotImplementedError

    def ports(self) -> dict[str, int]:
        """Expose public ports used by the running service.

        Returns
        -------
        dict
            A mapping containing ``omega_port`` and ``service_port`` values
            describing the control-plane and service bindings.
        """

        raise NotImplementedError
