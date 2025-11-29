"""Process helpers shared by Python and CLI interfaces."""
from __future__ import annotations

import os
import subprocess
import sys
from multiprocessing import Process
from pathlib import Path
from typing import Callable, Sequence

from .runtime import Runtime


def build_runtime_env(runtime: Runtime) -> dict[str, str]:
    """Construct environment variables for spawned services."""

    env: dict[str, str] = dict(os.environ)
    if runtime.env:
        env.update(runtime.env)
    env.update(
        {
            "OMEGASERVE_HOST": runtime.host,
            "OMEGASERVE_OMEGA_PORT": str(runtime.omega_port),
            "OMEGASERVE_SERVICE_PORT": str(runtime.service_port),
        }
    )
    return env


def launch_service_process(
    script_path: Path,
    hydra_overrides: Sequence[str],
    runtime: Runtime,
) -> subprocess.Popen:
    """Spawn a Hydra-wrapped service as a subprocess."""

    stdout = stderr = None
    log_handle = None
    if runtime.log_path:
        log_handle = open(runtime.log_path, "ab")
        stdout = stderr = log_handle

    process = subprocess.Popen(
        [sys.executable, str(script_path), *hydra_overrides],
        env=build_runtime_env(runtime),
        stdout=stdout,
        stderr=stderr,
    )

    if log_handle:
        process._omegaserve_log_handle = log_handle  # type: ignore[attr-defined]

    return process


def run_service_process(
    script_path: Path,
    hydra_overrides: Sequence[str],
    runtime: Runtime,
) -> int:
    """Run a service subprocess to completion and return its exit code."""

    process = launch_service_process(script_path, hydra_overrides, runtime)
    return monitor_process(process)


def _run_callable_service(service: Callable, config, runtime: Runtime) -> None:
    service(config, runtime)


def launch_callable_service(
    service: Callable,
    config,
    runtime: Runtime,
) -> Process:
    """Fork the current process to execute a Python callable service."""

    proc = Process(target=_run_callable_service, args=(service, config, runtime))
    proc.start()
    return proc


def monitor_process(process: subprocess.Popen | Process) -> int:
    """Wait for a managed process to finish and return its exit code."""

    exit_code: int
    if hasattr(process, "wait"):
        exit_code = process.wait()  # type: ignore[assignment]
        log_handle = getattr(process, "_omegaserve_log_handle", None)
        if log_handle:
            log_handle.close()
    else:
        process.join()
        exit_code = process.exitcode or 0
    return exit_code
