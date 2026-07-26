"""Deriva relatório Markdown de um ou mais datasets JSONL validados."""

from __future__ import annotations

import argparse
import statistics
from collections import defaultdict
from pathlib import Path

from benchmarks.schema import BenchmarkRecord


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-cv", type=float, default=5.0)
    return parser.parse_args()


def percentile_95(values: list[float]) -> float:
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[94]


def outlier_count(values: list[float]) -> int:
    if len(values) < 4:
        return 0
    quartiles = statistics.quantiles(values, n=4, method="inclusive")
    low = quartiles[0] - 1.5 * (quartiles[2] - quartiles[0])
    high = quartiles[2] + 1.5 * (quartiles[2] - quartiles[0])
    return sum(value < low or value > high for value in values)


def read_records(paths: list[Path]) -> list[BenchmarkRecord]:
    records: list[BenchmarkRecord] = []
    for path in paths:
        with path.open(encoding="utf-8") as stream:
            records.extend(
                BenchmarkRecord.model_validate_json(line) for line in stream if line.strip()
            )
    return records


def main() -> int:
    args = parse_args()
    records = read_records(args.inputs)
    measured = [record for record in records if record.execution_type != "warmup"]
    groups: dict[tuple[str, str, str, str, str], list[BenchmarkRecord]] = defaultdict(list)
    for record in measured:
        key = (
            record.run_id,
            record.engine,
            record.engine_version,
            record.case,
            record.execution_type,
        )
        groups[key].append(record)

    rows = []
    invalid_cv = []
    for key, group in sorted(groups.items()):
        values = [record.duration_ms for record in group]
        mean = statistics.fmean(values)
        cv = 0.0 if len(values) == 1 or mean == 0 else statistics.pstdev(values) / mean * 100
        row = {
            "run_id": key[0],
            "engine": f"{key[1]} {key[2]}",
            "case": key[3],
            "execution": key[4],
            "count": len(values),
            "minimum": min(values),
            "median": statistics.median(values),
            "p95": percentile_95(values),
            "cv": cv,
            "outliers": outlier_count(values),
        }
        rows.append(row)
        if cv > args.max_cv:
            invalid_cv.append((key[0], key[3], cv))

    run_records = {record.run_id: record for record in records}
    lines = [
        "# Relatório de benchmark da engine",
        "",
        "> Gerado automaticamente a partir dos dados JSONL validados.",
        "",
        "## Linhagem",
        "",
        "| run_id | Git SHA | fonte | ambiente |",
        "| --- | --- | --- | --- |",
    ]
    for run_id, record in sorted(run_records.items()):
        dirty = " + alterações locais" if record.git_dirty else ""
        lines.append(
            f"| `{run_id}` | `{record.git_sha[:12]}`{dirty} | "
            f"`{record.source_sha256[:12]}` | {record.runtime}, "
            f"{record.operating_system}, {record.hardware.architecture}, "
            f"{record.hardware.logical_cpus or '?'} CPUs lógicas |"
        )

    lines.extend(
        [
            "",
            "## Resultados",
            "",
            "| run_id | engine | tipo | caso | n | mín. ms | mediana ms | p95 ms | CV | outliers |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['run_id']}` | {row['engine']} | {row['execution']} | "
            f"{row['case']} | {row['count']} | "
            f"{row['minimum']:.2f} | {row['median']:.2f} | {row['p95']:.2f} | "
            f"{row['cv']:.2f}% | {row['outliers']} |"
        )

    valid = not invalid_cv
    v2_records = [record for record in measured if record.engine == "v2"]
    latest_v2_run_id = (
        max(v2_records, key=lambda record: record.captured_at).run_id if v2_records else None
    )
    target_rows = [
        row
        for row in rows
        if row["run_id"] == latest_v2_run_id
        and row["engine"].startswith("v2 ")
        and row["execution"] == "measure"
    ]
    performance_pass = bool(target_rows) and all(
        row["median"] < 500 and row["p95"] < 650 for row in target_rows
    )
    webgl_records = [record for record in measured if record.execution_type == "gpu"]
    latest_webgl_run_id = (
        max(webgl_records, key=lambda record: record.captured_at).run_id if webgl_records else None
    )
    webgl_rows = [
        row
        for row in rows
        if row["run_id"] == latest_webgl_run_id
        and row["engine"].startswith("webgl ")
        and row["execution"] == "gpu"
    ]
    webgl_pass = bool(webgl_rows) and all(row["median"] < 100 for row in webgl_rows)
    v2_gate = (
        "aprovada" if performance_pass else ("não atingida" if target_rows else "não aplicável")
    )
    webgl_gate = "aprovada" if webgl_pass else ("não atingida" if webgl_rows else "não aplicável")

    run_order = sorted(
        {record.run_id: record.captured_at for record in records},
        key=lambda run_id: run_records[run_id].captured_at,
    )
    if len(run_order) >= 2:
        first_run, last_run = run_order[0], run_order[-1]
        first_rows = {
            row["case"]: row
            for row in rows
            if row["run_id"] == first_run and row["execution"] != "export"
        }
        last_rows = {
            row["case"]: row
            for row in rows
            if row["run_id"] == last_run and row["execution"] != "export"
        }
        comparable = sorted(first_rows.keys() & last_rows.keys())
        lines.extend(
            [
                "",
                "## Comparação entre primeiro e último run",
                "",
                "| caso | baseline ms | atual ms | redução da mediana |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        first_engine = next(row["engine"] for row in rows if row["run_id"] == first_run).split()[0]
        last_engine = next(row["engine"] for row in rows if row["run_id"] == last_run).split()[0]
        if first_engine != last_engine:
            lines.extend(
                [
                    "",
                    "> Comparação cruzada de núcleos: CPU inclui a geração da imagem;",
                    "> GPU mede apenas o shader sincronizado. A exportação aparece separada;",
                    "> esses números não representam a mesma latência end-to-end.",
                    "",
                ]
            )
        for case in comparable:
            before = first_rows[case]["median"]
            after = last_rows[case]["median"]
            reduction = (before - after) / before * 100
            lines.append(f"| {case} | {before:.2f} | {after:.2f} | {reduction:.1f}% |")

    lines.extend(
        [
            "",
            "## Portões de decisão",
            "",
            f"- Estabilidade (`CV ≤ {args.max_cv:.1f}%`): **{'aprovada' if valid else 'reprovada'}**.",
            f"- Meta V2 (mediana < 500 ms e p95 < 650 ms): **{v2_gate}**.",
            f"- Meta WebGL render-only (mediana < 100 ms): **{webgl_gate}**.",
            "- Performance é válida apenas para o ambiente registrado acima.",
            "",
        ]
    )
    if invalid_cv:
        lines.append("Runs que precisam ser repetidos:")
        lines.append("")
        for run_id, case, cv in invalid_cv:
            lines.append(f"- `{run_id}` / `{case}`: CV {cv:.2f}%")
        lines.append("")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(args.output)
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
