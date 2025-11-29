"""Public service interface for OmegaServe."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence

from omegaconf import DictConfig

from .runtime import Runtime, runtime_from_env
from .process import launch_callable_service, monitor_process, run_service_process


class Service(Protocol):
    """Callable protocol for user-defined services."""

    def __call__(self, config: DictConfig, runtime: Runtime):
        ...


def serve(service: Service, config: DictConfig, runtime: Runtime | None = None) -> int:
    """Execute the provided service in a managed child process.

    The helper resolves runtime information, forks the current process, and
    blocks until the child exits, returning its exit code to the caller.
    """

    runtime = runtime or runtime_from_env()
    proc = launch_callable_service(service, config, runtime)
    return monitor_process(proc)


def serve_script(script: str | Path, runtime: Runtime, overrides: Sequence[str] = ()) -> int:
    """Launch a Hydra service script as a subprocess and wait for completion."""

    return run_service_process(Path(script), overrides, runtime)
