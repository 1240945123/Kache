# Experiment Diff And D009/D010 Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add comparable experiment reports and selected-driver action timelines so D009/D010 optimization can proceed with measurable before/after evidence.

**Architecture:** Keep the work inside `demo/agent/evaluate_results.py` and its focused unittest. First convert current report data into structured objects, then format markdown from those objects, then add optional baseline diff and selected-driver timeline sections. Production decision logic is untouched.

**Tech Stack:** Python standard library, `unittest`, JSON/JSONL result files, markdown report output.

---

## File Structure

- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/evaluate_results.py`
  - Owns result-file reading, structured summary creation, markdown formatting, diff computation, selected-driver timeline formatting, and CLI flags.
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_evaluate_results.py`
  - Owns unit tests for summary construction, diff formatting, missing-driver handling, timeline diagnostics, and CLI-compatible report output.
- Generated during verification only: `E:/school/KACHE/.worktrees/layered-preference-strategy/docs/superpowers/experiments/*.md`
  - Do not manually edit generated reports except to inspect output.

## Task 1: Extract Structured Experiment Summary

**Files:**
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/evaluate_results.py`
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_evaluate_results.py`

- [ ] **Step 1: Write failing tests for structured report data**

Add these imports and tests to `test_evaluate_results.py`:

```python
from evaluate_results import build_experiment_summary
```

```python
def _write_basic_results(results_dir: Path) -> None:
    (results_dir / "monthly_income_202603.json").write_text(
        json.dumps(
            {
                "summary": {
                    "total_net_income_all_drivers": 100.0,
                    "total_preference_penalty": 20.0,
                    "failed_driver_count": 0,
                    "total_token_usage": {"total_tokens": 5},
                },
                "drivers": [
                    {
                        "driver_id": "D001",
                        "income": {
                            "gross_income": 200.0,
                            "cost": 50.0,
                            "preference_penalty": 20.0,
                            "net_income": 130.0,
                        },
                        "calculation_aborted": False,
                        "preference_check": {"rules": [{"rule": "sample"}]},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (results_dir / "run_summary_202603.json").write_text(
        json.dumps(
            {
                "simulate_time_seconds": 3.5,
                "simulation_duration_days": 30,
                "simulation_max_steps": 20000,
                "completed_steps": 42,
            }
        ),
        encoding="utf-8",
    )
    (results_dir / "actions_202603_D001_sample.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"action": {"action": "take_order"}, "result": {"accepted": True}}),
                json.dumps({"action": {"action": "wait"}, "result": {}}),
            ]
        ),
        encoding="utf-8",
    )


def test_build_experiment_summary_returns_structured_data(self):
    with tempfile.TemporaryDirectory() as tmp:
        results_dir = Path(tmp)
        _write_basic_results(results_dir)

        summary = build_experiment_summary(results_dir, experiment_id="unit-test")

    self.assertEqual(summary["experiment_id"], "unit-test")
    self.assertEqual(summary["summary"]["total_net_income_all_drivers"], 100.0)
    self.assertEqual(summary["summary"]["total_token_usage"]["total_tokens"], 5)
    self.assertEqual(summary["run_summary"]["completed_steps"], 42)
    self.assertEqual(summary["drivers"][0]["driver_id"], "D001")
    self.assertEqual(summary["drivers"][0]["actions"]["take_order"], 1)
    self.assertEqual(summary["drivers"][0]["actions"]["wait"], 1)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest demo\agent\test_evaluate_results.py -v
```

Expected: FAIL because `build_experiment_summary` is not defined.

- [ ] **Step 3: Implement structured summary**

In `evaluate_results.py`, add:

```python
def build_experiment_summary(results_dir: Path, *, experiment_id: str) -> dict[str, Any]:
    monthly = _read_json(results_dir / f"monthly_income_{MONTH}.json")
    run_summary_path = results_dir / f"run_summary_{MONTH}.json"
    run_summary = _read_json(run_summary_path) if run_summary_path.exists() else {}

    raw_summary = monthly.get("summary", {})
    summary = raw_summary if isinstance(raw_summary, dict) else {}
    raw_driver_rows = monthly.get("drivers") or monthly.get("driver_rows") or monthly.get("rows") or []
    driver_rows = raw_driver_rows if isinstance(raw_driver_rows, list) else []

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
        drivers.append(
            {
                "driver_id": driver_id,
                "gross": income.get("gross_income", ""),
                "cost": income.get("cost", ""),
                "penalty": income.get("preference_penalty", ""),
                "net": income.get("net_income", ""),
                "calculation_aborted": row.get("calculation_aborted", ""),
                "rules": len(rules) if isinstance(rules, list) else 0,
                "actions": dict(sorted(_action_counts(results_dir, driver_id).items())),
            }
        )

    return {
        "experiment_id": experiment_id,
        "summary": summary,
        "run_summary": run_summary,
        "drivers": drivers,
        "results_dir": str(results_dir),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
```

- [ ] **Step 4: Refactor `build_report` to use structured summary**

Replace the body of `build_report` with:

```python
def build_report(
    results_dir: Path,
    *,
    experiment_id: str,
    baseline_path: Path | None = None,
    timeline_driver_ids: list[str] | None = None,
) -> str:
    summary = build_experiment_summary(results_dir, experiment_id=experiment_id)
    return format_report(
        summary,
        baseline_path=baseline_path,
        timeline_driver_ids=timeline_driver_ids or [],
        results_dir=results_dir,
    )
```

Then add this formatter:

```python
def format_report(
    experiment: dict[str, Any],
    *,
    baseline_path: Path | None = None,
    timeline_driver_ids: list[str],
    results_dir: Path,
) -> str:
    summary = experiment.get("summary", {})
    run_summary = experiment.get("run_summary", {})
    lines = [
        f"# Experiment {experiment.get('experiment_id', '')}",
        "",
        "## Summary",
        "",
    ]
    for key in (
        "total_net_income_all_drivers",
        "total_preference_penalty",
        "failed_driver_count",
    ):
        lines.append(f"- {key}: {summary.get(key, '') if isinstance(summary, dict) else ''}")
    token_usage = summary.get("total_token_usage", {}) if isinstance(summary, dict) else {}
    if isinstance(token_usage, dict):
        lines.append(f"- total_token_usage.total_tokens: {token_usage.get('total_tokens', '')}")
    if isinstance(run_summary, dict):
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
    for row in experiment.get("drivers", []):
        actions = row.get("actions", {})
        action_text = ", ".join(f"{name}={count}" for name, count in sorted(actions.items()))
        lines.append(
            "| {driver_id} | {gross} | {cost} | {penalty} | {net} | {aborted} | {rules} | {actions} |".format(
                driver_id=row.get("driver_id", ""),
                gross=row.get("gross", ""),
                cost=row.get("cost", ""),
                penalty=row.get("penalty", ""),
                net=row.get("net", ""),
                aborted=row.get("calculation_aborted", ""),
                rules=row.get("rules", ""),
                actions=action_text,
            )
        )

    lines.extend(format_delta_section(experiment, baseline_path))
    for driver_id in timeline_driver_ids:
        lines.extend(format_driver_timeline(results_dir, driver_id))

    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- Source results directory: {experiment.get('results_dir', results_dir)}",
            f"- Generated at: {experiment.get('generated_at', '')}",
        ]
    )
    return "\n".join(lines) + "\n"
```

Add temporary stubs so Task 1 passes before later tasks fill them:

```python
def format_delta_section(experiment: dict[str, Any], baseline_path: Path | None) -> list[str]:
    return []


def format_driver_timeline(results_dir: Path, driver_id: str) -> list[str]:
    return []
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m unittest demo\agent\test_evaluate_results.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add demo/agent/evaluate_results.py demo/agent/test_evaluate_results.py
git commit -m "refactor: structure experiment report data"
```

## Task 2: Add Baseline Diff Computation

**Files:**
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/evaluate_results.py`
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_evaluate_results.py`

- [ ] **Step 1: Write failing diff tests**

Add these imports:

```python
from evaluate_results import compute_experiment_delta, format_delta_section
```

Add tests:

```python
def test_compute_experiment_delta_sorts_regressions_first(self):
    baseline = {
        "summary": {
            "total_net_income_all_drivers": 100.0,
            "total_preference_penalty": 20.0,
            "failed_driver_count": 0,
            "total_token_usage": {"total_tokens": 5},
        },
        "run_summary": {"completed_steps": 40, "simulate_time_seconds": 3.0},
        "drivers": [
            {"driver_id": "D001", "gross": 100.0, "cost": 10.0, "penalty": 5.0, "net": 85.0, "actions": {"wait": 1}},
            {"driver_id": "D002", "gross": 100.0, "cost": 10.0, "penalty": 2.0, "net": 88.0, "actions": {"wait": 1}},
        ],
    }
    current = {
        "summary": {
            "total_net_income_all_drivers": 80.0,
            "total_preference_penalty": 35.0,
            "failed_driver_count": 1,
            "total_token_usage": {"total_tokens": 9},
        },
        "run_summary": {"completed_steps": 42, "simulate_time_seconds": 3.5},
        "drivers": [
            {"driver_id": "D001", "gross": 100.0, "cost": 10.0, "penalty": 25.0, "net": 65.0, "actions": {"wait": 3}},
            {"driver_id": "D002", "gross": 120.0, "cost": 10.0, "penalty": 2.0, "net": 108.0, "actions": {"wait": 1}},
        ],
    }

    delta = compute_experiment_delta(current, baseline)

    self.assertEqual(delta["summary"]["total_net_income_all_drivers"], -20.0)
    self.assertEqual(delta["summary"]["total_preference_penalty"], 15.0)
    self.assertEqual(delta["summary"]["failed_driver_count"], 1.0)
    self.assertEqual(delta["summary"]["total_token_usage.total_tokens"], 4.0)
    self.assertEqual(delta["run_summary"]["completed_steps"], 2.0)
    self.assertEqual(delta["drivers"][0]["driver_id"], "D001")
    self.assertEqual(delta["drivers"][0]["penalty"], 20.0)
    self.assertEqual(delta["drivers"][0]["net"], -20.0)
```

```python
def test_format_delta_section_reads_json_baseline(self):
    with tempfile.TemporaryDirectory() as tmp:
        baseline_path = Path(tmp) / "baseline.json"
        baseline_path.write_text(
            json.dumps(
                {
                    "summary": {
                        "total_net_income_all_drivers": 100.0,
                        "total_preference_penalty": 20.0,
                        "failed_driver_count": 0,
                        "total_token_usage": {"total_tokens": 5},
                    },
                    "run_summary": {"completed_steps": 40},
                    "drivers": [
                        {"driver_id": "D001", "gross": 100.0, "cost": 10.0, "penalty": 5.0, "net": 85.0, "actions": {}}
                    ],
                }
            ),
            encoding="utf-8",
        )
        current = {
            "summary": {
                "total_net_income_all_drivers": 110.0,
                "total_preference_penalty": 15.0,
                "failed_driver_count": 0,
                "total_token_usage": {"total_tokens": 8},
            },
            "run_summary": {"completed_steps": 42},
            "drivers": [
                {"driver_id": "D001", "gross": 120.0, "cost": 10.0, "penalty": 3.0, "net": 107.0, "actions": {}}
            ],
        }

        lines = format_delta_section(current, baseline_path)

    text = "\n".join(lines)
    self.assertIn("## Delta", text)
    self.assertIn("total_net_income_all_drivers: +10.0", text)
    self.assertIn("| D001 | +20.0 | +0.0 | -2.0 | +22.0 |", text)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m unittest demo\agent\test_evaluate_results.py -v
```

Expected: FAIL because diff functions do not exist or return empty sections.

- [ ] **Step 3: Implement numeric helpers and diff**

Add to `evaluate_results.py`:

```python
def _as_float(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _signed(value: float) -> str:
    return f"{value:+.1f}"


def _summary_token_total(summary: dict[str, Any]) -> float:
    token_usage = summary.get("total_token_usage", {})
    if isinstance(token_usage, dict):
        return _as_float(token_usage.get("total_tokens"))
    return 0.0


def compute_experiment_delta(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_summary = current.get("summary", {})
    baseline_summary = baseline.get("summary", {})
    current_run = current.get("run_summary", {})
    baseline_run = baseline.get("run_summary", {})

    summary_delta = {
        "total_net_income_all_drivers": _as_float(current_summary.get("total_net_income_all_drivers")) - _as_float(baseline_summary.get("total_net_income_all_drivers")),
        "total_preference_penalty": _as_float(current_summary.get("total_preference_penalty")) - _as_float(baseline_summary.get("total_preference_penalty")),
        "failed_driver_count": _as_float(current_summary.get("failed_driver_count")) - _as_float(baseline_summary.get("failed_driver_count")),
        "total_token_usage.total_tokens": _summary_token_total(current_summary) - _summary_token_total(baseline_summary),
    }
    run_delta = {
        key: _as_float(current_run.get(key)) - _as_float(baseline_run.get(key))
        for key in ("simulate_time_seconds", "simulation_duration_days", "simulation_max_steps", "completed_steps")
        if key in current_run or key in baseline_run
    }

    baseline_drivers = {str(row.get("driver_id", "")): row for row in baseline.get("drivers", []) if isinstance(row, dict)}
    current_drivers = {str(row.get("driver_id", "")): row for row in current.get("drivers", []) if isinstance(row, dict)}
    driver_deltas: list[dict[str, Any]] = []
    missing: list[str] = []
    for driver_id in sorted(set(current_drivers) | set(baseline_drivers)):
        current_row = current_drivers.get(driver_id)
        baseline_row = baseline_drivers.get(driver_id)
        if current_row is None or baseline_row is None:
            missing.append(driver_id)
            continue
        actions = {}
        current_actions = current_row.get("actions", {})
        baseline_actions = baseline_row.get("actions", {})
        for name in sorted(set(current_actions) | set(baseline_actions)):
            actions[name] = _as_float(current_actions.get(name)) - _as_float(baseline_actions.get(name))
        driver_deltas.append(
            {
                "driver_id": driver_id,
                "gross": _as_float(current_row.get("gross")) - _as_float(baseline_row.get("gross")),
                "cost": _as_float(current_row.get("cost")) - _as_float(baseline_row.get("cost")),
                "penalty": _as_float(current_row.get("penalty")) - _as_float(baseline_row.get("penalty")),
                "net": _as_float(current_row.get("net")) - _as_float(baseline_row.get("net")),
                "actions": actions,
            }
        )
    driver_deltas.sort(key=lambda row: (-row["penalty"], row["net"], row["driver_id"]))
    return {"summary": summary_delta, "run_summary": run_delta, "drivers": driver_deltas, "missing_drivers": missing}
```

- [ ] **Step 4: Implement baseline loading and markdown section**

Add:

```python
def _load_baseline(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return _read_json(path)
    raise ValueError(f"Baseline must be a structured JSON summary: {path}")
```

Replace the `format_delta_section` stub with:

```python
def format_delta_section(experiment: dict[str, Any], baseline_path: Path | None) -> list[str]:
    if baseline_path is None:
        return []
    baseline = _load_baseline(baseline_path)
    delta = compute_experiment_delta(experiment, baseline)
    lines = [
        "",
        "## Delta",
        "",
        f"- baseline: {baseline_path}",
    ]
    for key, value in delta["summary"].items():
        lines.append(f"- {key}: {_signed(value)}")
    for key, value in delta["run_summary"].items():
        lines.append(f"- {key}: {_signed(value)}")
    if delta["missing_drivers"]:
        lines.append(f"- missing_drivers: {', '.join(delta['missing_drivers'])}")

    lines.extend(
        [
            "",
            "| driver_id | gross Δ | cost Δ | penalty Δ | net Δ | actions Δ |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in delta["drivers"]:
        action_text = ", ".join(f"{name}={_signed(value)}" for name, value in sorted(row["actions"].items()))
        lines.append(
            "| {driver_id} | {gross} | {cost} | {penalty} | {net} | {actions} |".format(
                driver_id=row["driver_id"],
                gross=_signed(row["gross"]),
                cost=_signed(row["cost"]),
                penalty=_signed(row["penalty"]),
                net=_signed(row["net"]),
                actions=action_text,
            )
        )
    return lines
```

- [ ] **Step 5: Add JSON sidecar writer to CLI**

In `main`, after writing markdown, also write the structured summary:

```python
summary = build_experiment_summary(args.results_dir, experiment_id=args.experiment_id)
report = format_report(
    summary,
    baseline_path=args.baseline,
    timeline_driver_ids=args.timeline_driver,
    results_dir=args.results_dir,
)
args.out_dir.mkdir(parents=True, exist_ok=True)
out_path = args.out_dir / f"{args.experiment_id}.md"
json_path = args.out_dir / f"{args.experiment_id}.json"
out_path.write_text(report, encoding="utf-8")
json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(out_path)
print(json_path)
```

Add arguments before `args = parser.parse_args()`:

```python
parser.add_argument("--baseline", type=Path, default=None)
parser.add_argument("--timeline-driver", action="append", default=[])
```

- [ ] **Step 6: Run tests**

Run:

```powershell
python -m unittest demo\agent\test_evaluate_results.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```powershell
git add demo/agent/evaluate_results.py demo/agent/test_evaluate_results.py
git commit -m "feat: add experiment delta reporting"
```

## Task 3: Add Selected-Driver Timeline Diagnostics

**Files:**
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/evaluate_results.py`
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_evaluate_results.py`

- [ ] **Step 1: Write failing timeline test**

Add import:

```python
from evaluate_results import format_driver_timeline
```

Add test:

```python
def test_format_driver_timeline_summarizes_actions(self):
    with tempfile.TemporaryDirectory() as tmp:
        results_dir = Path(tmp)
        (results_dir / "actions_202603_D009_sample.jsonl").write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "step": 1,
                            "driver_id": "D009",
                            "step_elapsed_minutes": 30,
                            "position_before": {"lat": 23.12, "lng": 113.28},
                            "position_after": {"lat": 23.12, "lng": 113.28},
                            "simulation_end_time": "2026-03-01 00:30",
                            "action": {"action": "wait", "params": {"duration_minutes": 30}},
                            "result": {"simulation_progress_minutes": 30},
                        }
                    ),
                    json.dumps(
                        {
                            "step": 2,
                            "driver_id": "D009",
                            "step_elapsed_minutes": 715,
                            "position_before": {"lat": 23.12, "lng": 113.28},
                            "position_after": {"lat": 23.41, "lng": 113.36},
                            "simulation_end_time": "2026-03-01 12:25",
                            "action": {"action": "take_order", "params": {"cargo_id": "220562"}},
                            "result": {
                                "accepted": True,
                                "cargo_id": "220562",
                                "simulation_progress_minutes": 745,
                                "pickup_deadhead_km": 57.99,
                                "haul_distance_km": 49.14,
                            },
                        }
                    ),
                ]
            ),
            encoding="utf-8",
        )

        lines = format_driver_timeline(results_dir, "D009")

    text = "\n".join(lines)
    self.assertIn("## Timeline D009", text)
    self.assertIn("| 1 | 30 | 2026-03-01 00:30 | wait |", text)
    self.assertIn("duration=30", text)
    self.assertIn("| 2 | 745 | 2026-03-01 12:25 | take_order |", text)
    self.assertIn("cargo=220562", text)
    self.assertIn("deadhead=57.99", text)
    self.assertIn("haul=49.14", text)
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
python -m unittest demo\agent\test_evaluate_results.py -v
```

Expected: FAIL because `format_driver_timeline` still returns an empty list.

- [ ] **Step 3: Implement timeline helpers**

Add:

```python
def _latest_action_file(results_dir: Path, driver_id: str) -> Path | None:
    action_files = sorted(results_dir.glob(f"actions_{MONTH}_{driver_id}_*.jsonl"))
    return action_files[-1] if action_files else None


def _position_text(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    lat = value.get("lat")
    lng = value.get("lng")
    if lat is None or lng is None:
        return ""
    return f"({lat},{lng})"


def _action_detail(record: dict[str, Any]) -> str:
    action = record.get("action", {})
    params = action.get("params", {}) if isinstance(action, dict) else {}
    result = record.get("result", {})
    if not isinstance(params, dict):
        params = {}
    if not isinstance(result, dict):
        result = {}
    parts: list[str] = []
    cargo_id = params.get("cargo_id") or result.get("cargo_id")
    if cargo_id:
        parts.append(f"cargo={cargo_id}")
    if "duration_minutes" in params:
        parts.append(f"duration={params.get('duration_minutes')}")
    if "target_lat" in params and "target_lng" in params:
        parts.append(f"target=({params.get('target_lat')},{params.get('target_lng')})")
    if "accepted" in result:
        parts.append(f"accepted={result.get('accepted')}")
    if "pickup_deadhead_km" in result:
        parts.append(f"deadhead={result.get('pickup_deadhead_km')}")
    if "haul_distance_km" in result:
        parts.append(f"haul={result.get('haul_distance_km')}")
    return ", ".join(parts)
```

- [ ] **Step 4: Implement timeline formatter**

Replace the `format_driver_timeline` stub:

```python
def format_driver_timeline(results_dir: Path, driver_id: str) -> list[str]:
    action_file = _latest_action_file(results_dir, driver_id)
    lines = [
        "",
        f"## Timeline {driver_id}",
        "",
    ]
    if action_file is None:
        lines.append(f"- No action log found for {driver_id}")
        return lines

    lines.extend(
        [
            f"- Source action file: {action_file.name}",
            "",
            "| step | minute | wall_time | action | elapsed | before | after | details |",
            "| ---: | ---: | --- | --- | ---: | --- | --- | --- |",
        ]
    )
    with action_file.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            record = json.loads(line)
            action = record.get("action", {})
            action_name = action.get("action") if isinstance(action, dict) else action
            result = record.get("result", {})
            minute = result.get("simulation_progress_minutes", "") if isinstance(result, dict) else ""
            lines.append(
                "| {step} | {minute} | {wall_time} | {action} | {elapsed} | {before} | {after} | {details} |".format(
                    step=record.get("step", ""),
                    minute=minute,
                    wall_time=record.get("simulation_end_time", ""),
                    action=action_name or "",
                    elapsed=record.get("step_elapsed_minutes", ""),
                    before=_position_text(record.get("position_before")),
                    after=_position_text(record.get("position_after")),
                    details=_action_detail(record),
                )
            )
    return lines
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m unittest demo\agent\test_evaluate_results.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add demo/agent/evaluate_results.py demo/agent/test_evaluate_results.py
git commit -m "feat: add driver action timelines"
```

## Task 4: Verify CLI Output Against Current Results

**Files:**
- Modify only if tests reveal a formatting bug:
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/evaluate_results.py`
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_evaluate_results.py`
- Generated:
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/docs/superpowers/experiments/2026-05-14-diff-diagnostics-local.md`
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/docs/superpowers/experiments/2026-05-14-diff-diagnostics-local.json`

- [ ] **Step 1: Run all agent unit tests**

Run from `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent`:

```powershell
python -m unittest discover -s . -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 2: Generate a report with D009/D010 timelines**

Run from `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent`:

```powershell
python evaluate_results.py --results-dir ..\results --out-dir ..\..\docs\superpowers\experiments --experiment-id 2026-05-14-diff-diagnostics-local --timeline-driver D009 --timeline-driver D010
```

Expected: prints both `.md` and `.json` paths.

- [ ] **Step 3: Inspect generated report sections**

Run:

```powershell
rg -n "## Summary|## Drivers|## Timeline D009|## Timeline D010|Source action file" E:\school\KACHE\.worktrees\layered-preference-strategy\docs\superpowers\experiments\2026-05-14-diff-diagnostics-local.md
```

Expected: all headings are present.

- [ ] **Step 4: Generate a self-baseline delta report**

Run:

```powershell
python evaluate_results.py --results-dir ..\results --out-dir ..\..\docs\superpowers\experiments --experiment-id 2026-05-14-diff-diagnostics-self-delta --baseline ..\..\docs\superpowers\experiments\2026-05-14-diff-diagnostics-local.json --timeline-driver D009 --timeline-driver D010
```

Expected: generated report contains `## Delta` and near-zero deltas because the same results are compared to themselves.

- [ ] **Step 5: Inspect delta section**

Run:

```powershell
rg -n "## Delta|total_net_income_all_drivers|total_preference_penalty|completed_steps" E:\school\KACHE\.worktrees\layered-preference-strategy\docs\superpowers\experiments\2026-05-14-diff-diagnostics-self-delta.md
```

Expected: delta section exists and shows signed values.

- [ ] **Step 6: Commit generated diagnostic reports if useful**

If the generated reports are concise enough to keep as experiment evidence, run:

```powershell
git add demo/agent/evaluate_results.py demo/agent/test_evaluate_results.py docs/superpowers/experiments/2026-05-14-diff-diagnostics-local.md docs/superpowers/experiments/2026-05-14-diff-diagnostics-local.json docs/superpowers/experiments/2026-05-14-diff-diagnostics-self-delta.md docs/superpowers/experiments/2026-05-14-diff-diagnostics-self-delta.json
git commit -m "docs: record diff diagnostics experiment"
```

If the generated timeline markdown is too large, commit only code and tests:

```powershell
git add demo/agent/evaluate_results.py demo/agent/test_evaluate_results.py
git commit -m "feat: add experiment diagnostics reporting"
```

## Task 5: Use Diagnostics To Choose The First D009/D010 Scoring Fix

**Files:**
- Read:
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/docs/superpowers/experiments/2026-05-14-diff-diagnostics-local.md`
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/planner.py`
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/model_decision_service.py`
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/preference_parser.py`
- Do not modify production code in this task.

- [ ] **Step 1: Extract D009/D010 suspicious spans**

Run:

```powershell
rg -n "## Timeline D009|## Timeline D010|accepted=False|accepted=false|deadhead=|cargo=240646|reposition|wait" E:\school\KACHE\.worktrees\layered-preference-strategy\docs\superpowers\experiments\2026-05-14-diff-diagnostics-local.md
```

Expected: candidate lines showing waits, failed accepts, deadhead-heavy orders, and sequence/reposition behavior.

- [ ] **Step 2: Write an optimization note before coding**

Create or append to `docs/superpowers/experiments/2026-05-14-d009-d010-diagnostic-notes.md` with this structure:

```markdown
# D009/D010 Diagnostic Notes

## Current Evidence

- D009:
- D010:

## First Generic Fix Candidate

- Target rule type:
- Current behavior:
- Proposed generic behavior:
- Why this is not driver-ID hardcoding:

## Test Plan

- Unit test:
- Full smoke comparison:
```

- [ ] **Step 3: Commit diagnostic note**

Run:

```powershell
git add docs/superpowers/experiments/2026-05-14-d009-d010-diagnostic-notes.md
git commit -m "docs: identify first d009 d010 optimization target"
```

## Final Verification

- [ ] Run focused tests:

```powershell
python -m unittest demo\agent\test_evaluate_results.py -v
```

- [ ] Run full agent unit tests:

```powershell
python -m unittest discover -s demo\agent -p "test_*.py" -v
```

- [ ] Confirm no production decision hardcoding was introduced:

```powershell
rg -n "driver_id\s*==|D009|D010|240646" E:\school\KACHE\.worktrees\layered-preference-strategy\demo\agent --glob "!test_*.py"
```

Expected: no matches in production decision code. Mentions in tests or generated reports are acceptable.

- [ ] Confirm branch status:

```powershell
git status --short --branch
```

Expected: clean worktree after final commit.

