"""Contrato versionado dos dados brutos de benchmark."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HardwareInfo(BaseModel):
    """Informações suficientes para comparação, sem identificar a máquina."""

    architecture: str
    logical_cpus: int | None = Field(default=None, ge=1)
    power: Literal["ac", "battery", "unknown"] = "unknown"
    workload: Literal["dedicated", "shared", "unknown"] = "unknown"


class BenchmarkRecord(BaseModel):
    """Uma observação imutável produzida pelo runner."""

    schema_version: Literal["1.0"] = "1.0"
    run_id: str = Field(min_length=12, max_length=96)
    captured_at: datetime
    git_sha: str = Field(pattern=r"^[0-9a-f]{7,40}$")
    git_dirty: bool
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    engine: Literal["legacy", "v2", "webgl"]
    engine_version: str
    implementation: Literal["python", "cython", "webgl"] | None = None
    case: str
    config: dict[str, int | float | str | bool | None]
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    oversample: int = Field(ge=1)
    seed: int | None = Field(default=None, ge=0)
    execution_type: Literal["warmup", "measure", "gpu", "export"]
    iteration: int = Field(ge=1)
    duration_ms: float = Field(ge=0)
    rgb_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    python_version: str | None = None
    runtime: str
    operating_system: str
    hardware: HardwareInfo
