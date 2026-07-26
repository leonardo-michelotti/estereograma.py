"""Linhagem de código e ambiente sem coletar identificadores pessoais."""

from __future__ import annotations

import hashlib
import os
import platform
import subprocess
import sys
from pathlib import Path

from benchmarks.schema import HardwareInfo

ROOT = Path(__file__).resolve().parents[1]
ENGINE_SOURCE = ROOT / "app" / "stereogram" / "generator_v2.py"


def git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def source_sha256() -> str:
    return hashlib.sha256(ENGINE_SOURCE.read_bytes()).hexdigest()


def runtime_metadata(power: str, workload: str) -> dict[str, object]:
    return {
        "python_version": platform.python_version(),
        "runtime": f"{platform.python_implementation()} {sys.version_info.major}.{sys.version_info.minor}",
        "operating_system": f"{platform.system()} {platform.release()}",
        "hardware": HardwareInfo(
            architecture=platform.machine() or "unknown",
            logical_cpus=os.cpu_count(),
            power=power,
            workload=workload,
        ),
    }
