"""OmegaServe package scaffold.

This module exposes public interfaces for service hosting built around
``omegaconf``/``hydra`` configurations. The implementation is intentionally
minimal to keep the framework design flexible for future iterations.
"""

__version__ = "0.1.0"

from .runtime import Runtime, runtime_from_env
from .service import Service, serve, serve_script
from .api import ServiceController, ServiceStatus

__all__ = [
    "Runtime",
    "runtime_from_env",
    "Service",
    "serve",
    "serve_script",
    "ServiceController",
    "ServiceStatus",
]
