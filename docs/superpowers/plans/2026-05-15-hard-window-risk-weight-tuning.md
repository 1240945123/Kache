# Hard Window Risk Weight Tuning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tune the generic no-drive window risk penalty and keep it only if full replay score improves.

**Architecture:** The scoring module already detects candidates whose execution interval overlaps a hard `NO_DRIVE_WINDOW`. This plan changes only the generic penalty constant and evaluates the full monthly replay.

**Tech Stack:** Python unittest, local simulator under `demo/server`, monthly income calculator under `demo/calc_monthly_income.py`.

---

### Task 1: Tune Generic Risk Weight

**Files:**
- Modify: `demo/agent/scoring.py`
- Test: `demo/agent/test_scoring.py`

- [ ] **Step 1: Change the constant**

In `demo/agent/scoring.py`, set:

```python
HARD_NO_DRIVE_WINDOW_RISK_PENALTY = 2000.0
```

- [ ] **Step 2: Run focused scoring tests**

Run from `demo/agent`:

```bash
python -m unittest test_scoring.ScoringTest.test_hard_no_drive_window_risk_can_lower_crossing_candidate test_scoring.ScoringTest.test_sequence_deadline_risk_can_lower_late_candidate -v
```

Expected: both tests pass.

- [ ] **Step 3: Run full unit tests**

Run from `demo/agent`:

```bash
python -m unittest discover -v
```

Expected: 106 tests pass.

### Task 2: Full Replay Evaluation

**Files:**
- Create: `docs/superpowers/experiments/2026-05-15-hard-window-risk-weight-2000-local.md`
- Create: `docs/superpowers/experiments/2026-05-15-hard-window-risk-weight-2000-local.json`

- [ ] **Step 1: Run simulator**

Run from `demo/server`:

```bash
python main.py
```

Expected: exit code 0 and `demo/results/run_summary_202603.json` refreshed.

- [ ] **Step 2: Calculate monthly income**

Run from `demo`:

```bash
python calc_monthly_income.py
```

Expected: exit code 0 and `demo/results/monthly_income_202603.json` refreshed.

- [ ] **Step 3: Generate comparison report**

Run from `demo/agent`:

```bash
python evaluate_results.py --results-dir ..\results --out-dir ..\..\docs\superpowers\experiments --experiment-id 2026-05-15-hard-window-risk-weight-2000-local --baseline ..\..\docs\superpowers\experiments\2026-05-15-hard-window-risk-scoring-local.json --timeline-driver D005 --timeline-driver D007 --timeline-driver D010
```

Expected: report and JSON sidecar are created.

- [ ] **Step 4: Accept or revert**

If `total_net_income_all_drivers` is greater than `182696.6`, keep the constant. Otherwise restore:

```python
HARD_NO_DRIVE_WINDOW_RISK_PENALTY = 700.0
```

### Task 3: Final Verification And Commit

**Files:**
- Modify: `demo/agent/scoring.py`
- Create: experiment report files only if the tuning is accepted

- [ ] **Step 1: Run verification**

Run from `demo/agent`:

```bash
python -m unittest discover -v
```

Expected: 106 tests pass.

- [ ] **Step 2: Scan for hardcoding risk**

Run from repo root:

```bash
rg "D00|driver_id|cargo_id\s*==|cargo_id\s+in|司机|偏好" demo/agent --glob "!test_*.py"
```

Expected: no production scoring branch by specific driver or cargo ID.

- [ ] **Step 3: Commit accepted changes**

Run from repo root:

```bash
git add demo/agent/scoring.py docs/superpowers/specs/2026-05-15-hard-window-risk-weight-tuning-design.md docs/superpowers/plans/2026-05-15-hard-window-risk-weight-tuning.md docs/superpowers/experiments/2026-05-15-hard-window-risk-weight-2000-local.md docs/superpowers/experiments/2026-05-15-hard-window-risk-weight-2000-local.json
git commit -m "chore: tune hard window risk weight"
```

Expected: a commit containing only the accepted tuning and documentation.

## Self-Review

- The plan touches only one scoring constant plus documentation and reports.
- The accept/revert criterion is explicit.
- Commands are exact and scoped to the existing worktree.
