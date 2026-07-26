"""Monta uma sessão A/B cega entre PNGs da V2 e do laboratório WebGL."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
from pathlib import Path

CASES = {
    "coracao": ("04-v2-mosaico-fino.png", "webgl-heart.png"),
    "texto-3d": ("05-v2-texto-3d.png", "webgl-text-3d.png"),
    "esfera": ("06-v2-esfera.png", "webgl-sphere.png"),
}
ROOT = Path(__file__).resolve().parents[1]
GOLDENS = ROOT / "tests" / "fixtures" / "engine-v2.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--webgl-dir", required=True, type=Path)
    parser.add_argument("--session", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    return parser.parse_args()


def build_gallery(webgl_dir: Path, session: str, output: Path, mapping: Path) -> None:
    if output.exists() or mapping.exists():
        raise FileExistsError("a sessão é imutável; escolha novos caminhos")
    seed = int.from_bytes(hashlib.sha256(session.encode()).digest()[:8], "big")
    rng = random.Random(seed)
    assets = output.parent / f"{output.stem}-assets"
    assets.mkdir(parents=True, exist_ok=False)
    reveal: dict[str, dict[str, str]] = {}
    cards: list[str] = []
    case_order = list(CASES)
    rng.shuffle(case_order)
    for position, case in enumerate(case_order, 1):
        v2_name, webgl_name = CASES[case]
        sources = [("V2", GOLDENS / v2_name), ("WebGL", webgl_dir / webgl_name)]
        if not all(path.is_file() for _, path in sources):
            missing = [str(path) for _, path in sources if not path.is_file()]
            raise FileNotFoundError(", ".join(missing))
        rng.shuffle(sources)
        labels = ("A", "B")
        reveal[case] = {}
        panes = []
        for label, (engine, source) in zip(labels, sources, strict=True):
            filename = f"{position:02d}-{label.lower()}.png"
            shutil.copyfile(source, assets / filename)
            reveal[case][label] = engine
            panes.append(
                f'<figure><img src="{assets.name}/{filename}" alt="Opção {label} do caso {position}">'
                f"<figcaption>{label}</figcaption></figure>"
            )
        cards.append(
            f'<section><h2>Caso {position}</h2><div class="pair">{"".join(panes)}</div>'
            "<label>Mais fácil de fundir <select><option>—</option><option>A</option><option>B</option><option>Empate</option></select></label>"
            "<label>Profundidade mais clara <select><option>—</option><option>A</option><option>B</option><option>Empate</option></select></label>"
            "<label>Menos artefatos <select><option>—</option><option>A</option><option>B</option><option>Empate</option></select></label></section>"
        )

    html = f"""<!doctype html><html lang=\"pt-BR\"><meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width\"><title>Sessão A/B {session}</title>
<style>body{{font:16px system-ui;margin:0 auto;max-width:1400px;padding:32px;background:#f2efe6;color:#111}}
h1{{font-size:clamp(36px,6vw,72px)}}section{{border-top:1px solid;padding:32px 0}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
figure{{margin:0}}img{{display:block;width:100%;border:1px solid}}figcaption{{font:700 24px monospace;margin-top:8px}}
label{{display:inline-flex;gap:8px;margin:20px 24px 0 0}}@media(max-width:700px){{.pair{{grid-template-columns:1fr}}}}</style>
<h1>Avaliação cega da engine</h1><p>Sessão <code>{session}</code>. Veja cada imagem antes de escolher. Registre as respostas na ficha do estudo.</p>
{"".join(cards)}</html>"""
    output.write_text(html, encoding="utf-8", newline="\n")
    mapping.parent.mkdir(parents=True, exist_ok=True)
    mapping.write_text(
        json.dumps(
            {
                "session": session,
                "seed_sha256": hashlib.sha256(session.encode()).hexdigest(),
                "mapping": reveal,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build_gallery(args.webgl_dir, args.session, args.output, args.mapping)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
