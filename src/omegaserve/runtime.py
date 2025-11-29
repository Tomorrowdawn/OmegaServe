"""Runtime configuration dataclasses for OmegaServe.

Only structural definitions live here; concrete runtime provisioning logic
belongs in higher-level orchestration modules.
"""
from __future__ import annotations

import os
from typing import Mapping, Optional

import attrs


@attrs.define(auto_attribs=True)
class Runtime:
    """Runtime parameters injected into services.

    Attributes
    ----------
    host:
        Host address used to bind the serving API.
    omega_port:
        Preferred port for the OmegaServe control plane. Implementations may
        override this when performing automatic discovery.
    service_port:
        Preferred port for the managed service. Implementations may override
        this when performing automatic discovery.
    log_path:
        Optional file path for service stdout/stderr redirection.
    env:
        Optional environment variables provided to child processes.
    metadata:
        Free-form dictionary for implementation-specific runtime metadata
        such as allocation identifiers or deployment labels.
    """

    host: str = "::"
    omega_port: int = 0
    service_port: int = 0
    log_path: Optional[str] = None
    env: Optional[Mapping[str, str]] = None
    metadata: Mapping[str, str] = attrs.field(factory=dict)


def runtime_from_env(env: Optional[Mapping[str, str]] = None) -> Runtime:
    """Construct a :class:`Runtime` object from environment variables.

    The helper keeps host strings untouched (including IPv6 literals without
    brackets) to reflect the raw address values provided by callers. Port
    values default to ``0`` when absent to allow later automatic allocation.
    """

    env = env or os.environ
    return Runtime(
        host=env.get("OMEGASERVE_HOST", "::"),
        omega_port=int(env.get("OMEGASERVE_OMEGA_PORT", 0)),
        service_port=int(env.get("OMEGASERVE_SERVICE_PORT", 0)),
    )
