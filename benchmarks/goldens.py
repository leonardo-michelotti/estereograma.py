"""Cria uma vez ou verifica as fixtures RGB da engine."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from benchmarks.suites import golden_cases

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "engine-v2.0"
MANIFEST = FIXTURES / "manifest.json"


def rgb_hash(image: Image.Image) -> str:
    return hashlib.sha256(np.asarray(image.convert("RGB"), dtype=np.uint8).tobytes()).hexdigest()


def write_initial_goldens() -> None:
    if MANIFEST.exists():
        raise SystemExit(
            "recusado: goldens já existem; atualização exige ADR e nova versão da engine"
        )
    FIXTURES.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, dict[str, object]] = {}
    for case in golden_cases():
        image = case.render().convert("RGB")
        filename = f"{case.slug}.png"
        image.save(FIXTURES / filename, format="PNG", optimize=True)
        manifest[case.slug] = {
            "engine": case.engine,
            "engine_version": case.engine_version,
            "rgb_sha256": rgb_hash(image),
            "file": filename,
            "config": case.serialized_config(),
        }
        print(f"criado: {filename}")
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_goldens() -> list[str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in golden_cases():
        expected = manifest[case.slug]
        fixture = Image.open(FIXTURES / expected["file"]).convert("RGB")
        generated = case.render().convert("RGB")
        if not np.array_equal(np.asarray(fixture), np.asarray(generated)):
            failures.append(case.slug)
        if rgb_hash(generated) != expected["rgb_sha256"]:
            failures.append(f"{case.slug}:hash")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-initial", action="store_true")
    args = parser.parse_args()
    if args.write_initial:
        write_initial_goldens()
        return 0
    failures = verify_goldens()
    if failures:
        print("divergências: " + ", ".join(failures))
        return 1
    print("goldens: pixels RGB idênticos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
