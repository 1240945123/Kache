from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


MONTH = "202603"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _action_counts(results_dir: Path, driver_id: str) -> Counter[str]:
    action_files = sorted(results_dir.glob(f"actions_{MONTH}_{driver_id}_*.jsonl"))
    if not action_files:
        return Counter()

    counts: Counter[str] = Counter()
    with action_files[-1].open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            action_value = record.get("action", {})
            if isinstance(action_value, dict):
                action_name = action_value.get("action")
            else:
                action_name = action_value
            if not action_name:
                continue
            counts[str(action_name)] += 1
            if action_name == "take_order" and record.get("result", {}).get("accepted") is False:
                counts["accepted_false"] += 1
    return counts


def build_experiment_summary(results_dir: Path, *, experiment_id: str) -> dict[str, Any]:
    monthly = _read_json(results_dir / f"monthly_income_{MONTH}.json")
    run_summary_path = results_dir / f"run_summary_{MONTH}.json"
    run_summary = _read_json(run_summary_path) if run_summary_path.exists() else {}

    summary = monthly.get("summary", {})
    driver_rows = monthly.get("drivers") or monthly.get("driver_rows") or monthly.get("rows") or []
    drivers: list[dict[str, Any]] = []
    for row in driver_rows:
        driver_id = str(row.get("driver_id", ""))
        income = row.get("income", {})
        if not isinstance(income, dict):
            income = {}
        preference_check = row.get("preference_check", {})
        rules = preference_check.get("rules", []) if isinstance(preference_check, dict) else []
        drivers.append(
            {
                "driver_id": driver_id,
                "gross": income.get("gross_income", ""),
                "cost": income.get("cost", ""),
                "penalty": income.get("preference_penalty", ""),
                "net": income.get("net_income", ""),
                "calculation_aborted": row.get("calculation_aborted", ""),
                "rules": rules,
                "actions": dict(sorted(_action_counts(results_dir, driver_id).items())),
            }
        )

    return {
        "experiment_id": experiment_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "results_dir": results_dir,
        "summary": summary,
        "run_summary": run_summary,
        "drivers": drivers,
    }


def format_delta_section(experiment: dict[str, Any], baseline_path: Path | None) -> list[str]:
    return []


def format_driver_timeline(results_dir: Path, driver_id: str) -> list[str]:
    return []


def format_report(
    experiment: dict[str, Any],
    *,
    baseline_path: Path | None = None,
    timeline_driver_ids: list[str] | None = None,
) -> str:
    experiment_id = experiment["experiment_id"]
    results_dir = experiment["results_dir"]
    summary = experiment.get("summary", {})
    run_summary = experiment.get("run_summary", {})
    driver_rows = experiment.get("drivers", [])
    lines = [
        f"# Experiment {experiment_id}",
        "",
        "## Summary",
        "",
    ]
    for key in (
        "total_net_income_all_drivers",
        "total_preference_penalty",
        "failed_driver_count",
    ):
        lines.append(f"- {key}: {summary.get(key, '')}")
    token_usage = summary.get("total_token_usage", {})
    if isinstance(token_usage, dict):
        lines.append(f"- total_token_usage.total_tokens: {token_usage.get('total_tokens', '')}")
    if run_summary:
        for key in ("simulate_time_seconds", "simulation_duration_days", "simulation_max_steps", "completed_steps"):
            if key in run_summary:
                lines.append(f"- {key}: {run_summary.get(key, '')}")

    lines.extend(
        [
            "",
            "## Drivers",
            "",
            "| driver_id | gross | cost | penalty | net | calculation_aborted | rules | actions |",
            "| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
        ]
    )
    for row in driver_rows:
        driver_id = str(row.get("driver_id", ""))
        counts = row.get("actions", {})
        rules = row.get("rules", [])
        action_text = ", ".join(f"{name}={count}" for name, count in sorted(counts.items()))
        lines.append(
            "| {driver_id} | {gross} | {cost} | {penalty} | {net} | {aborted} | {rules} | {actions} |".format(
                driver_id=driver_id,
                gross=row.get("gross", ""),
                cost=row.get("cost", ""),
                penalty=row.get("penalty", ""),
                net=row.get("net", ""),
                aborted=row.get("calculation_aborted", ""),
                rules=len(rules),
                actions=action_text,
            )
        )

    lines.extend(format_delta_section(experiment, baseline_path))
    for driver_id in timeline_driver_ids or []:
        lines.extend(format_driver_timeline(results_dir, driver_id))

    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- Source results directory: {results_dir}",
            f"- Generated at: {experiment.get('generated_at', '')}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_report(
    results_dir: Path,
    *,
    experiment_id: str,
    baseline_path: Path | None = None,
    timeline_driver_ids: list[str] | None = None,
) -> str:
    experiment = build_experiment_summary(results_dir, experiment_id=experiment_id)
    return format_report(experiment, baseline_path=baseline_path, timeline_driver_ids=timeline_driver_ids)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a markdown experiment report from agent result files.")
    parser.add_argument("--results-dir", type=Path, default=Path("../results"))
    parser.add_argument("--out-dir", type=Path, default=Path("../../docs/superpowers/experiments"))
    parser.add_argument("--experiment-id", default=datetime.now().strftime("%Y%m%d-%H%M%S"))
    args = parser.parse_args()

    report = build_report(args.results_dir, experiment_id=args.experiment_id)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{args.experiment_id}.md"
    out_path.write_text(report, encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
