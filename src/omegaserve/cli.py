"""Command line interface for OmegaServe."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from omegaconf import OmegaConf

from .runtime import Runtime
from .process import run_service_process


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="omgserve",
        description="Launch OmegaServe-managed Hydra services",
        add_help=True,
    )
    parser.add_argument("runtime", nargs="*", help="Runtime overrides (host=, port=, etc.) before script path")
    parser.add_argument("script", help="Path to Hydra-wrapped service script")
    parser.add_argument("overrides", nargs=argparse.REMAINDER, help="Hydra-style configuration overrides")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    runtime_conf = OmegaConf.from_dotlist([arg for arg in args.runtime if "=" in arg])
    runtime = Runtime(
        host=runtime_conf.get("host", "::"),
        omega_port=int(runtime_conf.get("omega_port", 0)),
        service_port=int(runtime_conf.get("service_port", 0)),
    )

    script_path = Path(args.script)
    if not script_path.exists():
        raise FileNotFoundError(f"Service script not found: {script_path}")

    hydra_overrides = [override for override in args.overrides if override]

    return run_service_process(script_path, hydra_overrides, runtime)


if __name__ == "__main__":
    sys.exit(main())
