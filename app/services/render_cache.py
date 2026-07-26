"""Cache temporário e limitado para PNGs gerados."""

from __future__ import annotations

import re
import tempfile
import time
from pathlib import Path


RENDER_ID = re.compile(r"^[a-f0-9]{32}(?:-depth)?$")


class RenderCache:
    def __init__(
        self,
        root: Path | None = None,
        *,
        ttl_seconds: int = 30 * 60,
        max_bytes: int = 100 * 1024 * 1024,
    ) -> None:
        self.root = root or Path(tempfile.gettempdir()) / "estereograma-renders"
        self.ttl_seconds = ttl_seconds
        self.max_bytes = max_bytes
        self.root.mkdir(parents=True, exist_ok=True)

    def get(self, render_id: str) -> Path | None:
        path = self._path(render_id)
        if not path.is_file():
            return None
        if time.time() - path.stat().st_mtime > self.ttl_seconds:
            path.unlink(missing_ok=True)
            return None
        return path

    def put(self, render_id: str, content: bytes) -> Path:
        path = self._path(render_id)
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(content)
        temporary.replace(path)
        self.cleanup()
        return path

    def cleanup(self) -> None:
        now = time.time()
        files = sorted(
            (p for p in self.root.glob("*.png") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
        )
        for path in list(files):
            if now - path.stat().st_mtime > self.ttl_seconds:
                path.unlink(missing_ok=True)
                files.remove(path)

        total = sum(path.stat().st_size for path in files)
        for path in files:
            if total <= self.max_bytes:
                break
            size = path.stat().st_size
            path.unlink(missing_ok=True)
            total -= size

    def _path(self, render_id: str) -> Path:
        if not RENDER_ID.fullmatch(render_id):
            raise ValueError("Identificador de render inválido.")
        return self.root / f"{render_id}.png"
