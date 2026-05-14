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
    if not isinstance(driver_rows, list):
        driver_rows = []
    drivers: list[dict[str, Any]] = []
    for row in driver_rows:
        if not isinstance(row, dict):
            continue
        driver_id = str(row.get("driver_id", ""))
        income = row.get("income", {})
        if not isinstance(income, dict):
            income = {}
        preference_check = row.get("preference_check", {})
        rules = preference_check.get("rules", []) if isinstance(preference_check, dict) else []
        rule_count = len(rules) if isinstance(rules, list) else 0
        drivers.append(
            {
                "driver_id": driver_id,
                "gross": income.get("gross_income", ""),
                "cost": income.get("cost", ""),
                "penalty": income.get("preference_penalty", ""),
                "net": income.get("net_income", ""),
                "calculation_aborted": row.get("calculation_aborted", ""),
                "rules": rule_count,
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


def _as_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _signed(value: float) -> str:
    return f"{value:+.1f}"


def _summary_token_total(summary: dict[str, Any]) -> float:
    token_usage = summary.get("total_token_usage", {})
    if not isinstance(token_usage, dict):
        return 0.0
    return _as_float(token_usage.get("total_tokens"))


def compute_experiment_delta(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_summary = current.get("summary", {})
    if not isinstance(current_summary, dict):
        current_summary = {}
    baseline_summary = baseline.get("summary", {})
    if not isinstance(baseline_summary, dict):
        baseline_summary = {}

    summary_keys = (
        "total_net_income_all_drivers",
        "total_preference_penalty",
        "failed_driver_count",
    )
    summary_delta = {
        key: _as_float(current_summary.get(key)) - _as_float(baseline_summary.get(key)) for key in summary_keys
    }
    summary_delta["total_token_usage.total_tokens"] = _summary_token_total(current_summary) - _summary_token_total(
        baseline_summary
    )

    current_run_summary = current.get("run_summary", {})
    if not isinstance(current_run_summary, dict):
        current_run_summary = {}
    baseline_run_summary = baseline.get("run_summary", {})
    if not isinstance(baseline_run_summary, dict):
        baseline_run_summary = {}
    run_summary_delta = {}
    for key in ("completed_steps", "simulate_time_seconds"):
        if key in current_run_summary or key in baseline_run_summary:
            run_summary_delta[key] = _as_float(current_run_summary.get(key)) - _as_float(baseline_run_summary.get(key))

    def rows_by_driver(experiment: dict[str, Any]) -> dict[str, dict[str, Any]]:
        rows = experiment.get("drivers", [])
        if not isinstance(rows, list):
            return {}
        by_driver = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            driver_id = str(row.get("driver_id", ""))
            if driver_id:
                by_driver[driver_id] = row
        return by_driver

    current_drivers = rows_by_driver(current)
    baseline_drivers = rows_by_driver(baseline)
    driver_deltas = []
    for driver_id in sorted(set(current_drivers) | set(baseline_drivers)):
        current_row = current_drivers.get(driver_id, {})
        baseline_row = baseline_drivers.get(driver_id, {})
        current_actions = current_row.get("actions", {})
        if not isinstance(current_actions, dict):
            current_actions = {}
        baseline_actions = baseline_row.get("actions", {})
        if not isinstance(baseline_actions, dict):
            baseline_actions = {}
        action_delta = {
            action: _as_float(current_actions.get(action)) - _as_float(baseline_actions.get(action))
            for action in sorted(set(current_actions) | set(baseline_actions))
        }
        driver_deltas.append(
            {
                "driver_id": driver_id,
                "gross": _as_float(current_row.get("gross")) - _as_float(baseline_row.get("gross")),
                "cost": _as_float(current_row.get("cost")) - _as_float(baseline_row.get("cost")),
                "penalty": _as_float(current_row.get("penalty")) - _as_float(baseline_row.get("penalty")),
                "net": _as_float(current_row.get("net")) - _as_float(baseline_row.get("net")),
                "actions": action_delta,
            }
        )
    driver_deltas.sort(key=lambda row: (-row["penalty"], row["net"], row["driver_id"]))

    return {
        "summary": summary_delta,
        "run_summary": run_summary_delta,
        "drivers": driver_deltas,
    }


def _load_baseline(path: Path) -> dict[str, Any]:
    return _read_json(path)


def format_delta_section(experiment: dict[str, Any], baseline_path: Path | None) -> list[str]:
    if baseline_path is None:
        return []
    baseline = _load_baseline(baseline_path)
    delta = compute_experiment_delta(experiment, baseline)
    lines = [
        "",
        "## Delta",
        "",
    ]
    for key in (
        "total_net_income_all_drivers",
        "total_preference_penalty",
        "failed_driver_count",
        "total_token_usage.total_tokens",
    ):
        lines.append(f"- {key}: {_signed(delta['summary'].get(key, 0.0))}")
    for key in ("completed_steps", "simulate_time_seconds"):
        if key in delta["run_summary"]:
            lines.append(f"- {key}: {_signed(delta['run_summary'].get(key, 0.0))}")

    lines.extend(
        [
            "",
            "| driver_id | gross | cost | penalty | net | actions Δ |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in delta["drivers"]:
        actions = row.get("actions", {})
        if not isinstance(actions, dict):
            actions = {}
        action_text = ", ".join(f"{name}={_signed(_as_float(value))}" for name, value in sorted(actions.items()))
        lines.append(
            "| {driver_id} | {gross} | {cost} | {penalty} | {net} | {actions} |".format(
                driver_id=row.get("driver_id", ""),
                gross=_signed(row.get("gross", 0.0)),
                cost=_signed(row.get("cost", 0.0)),
                penalty=_signed(row.get("penalty", 0.0)),
                net=_signed(row.get("net", 0.0)),
                actions=action_text,
            )
        )
    return lines


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
        action_text = ", ".join(f"{name}={count}" for name, count in sorted(counts.items()))
        lines.append(
            "| {driver_id} | {gross} | {cost} | {penalty} | {net} | {aborted} | {rules} | {actions} |".format(
                driver_id=driver_id,
                gross=row.get("gross", ""),
                cost=row.get("cost", ""),
                penalty=row.get("penalty", ""),
                net=row.get("net", ""),
                aborted=row.get("calculation_aborted", ""),
                rules=row.get("rules", 0),
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
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--timeline-driver", action="append", default=[])
    args = parser.parse_args()

    experiment = build_experiment_summary(args.results_dir, experiment_id=args.experiment_id)
    report = format_report(
        experiment,
        baseline_path=args.baseline,
        timeline_driver_ids=args.timeline_driver,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{args.experiment_id}.md"
    json_path = args.out_dir / f"{args.experiment_id}.json"
    out_path.write_text(report, encoding="utf-8")
    json_path.write_text(json.dumps(experiment, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(out_path)
    print(json_path)


if __name__ == "__main__":
    main()
