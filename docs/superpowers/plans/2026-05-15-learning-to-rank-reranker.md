# Learning-to-Rank Reranker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a small generic Learning-to-Rank reranker after current scoring and keep it only if full replay improves.

**Architecture:** `scoring.py` keeps producing base `ScoredCandidate` objects. A new `ltr_ranker.py` module computes generic feature adjustments and returns reranked scored candidates. `model_decision_service.py` applies the reranker after scoring.

**Tech Stack:** Python standard library, `unittest`, local simulator.

---

### Task 1: LTR Unit Tests

**Files:**
- Create: `demo/agent/test_ltr_ranker.py`
- Create: `demo/agent/ltr_ranker.py`

- [ ] **Step 1: Write failing reranker tests**

Create `demo/agent/test_ltr_ranker.py` with tests that build two `ScoredCandidate` objects and assert that a higher value-density candidate can outrank a slightly higher base-score candidate.

- [ ] **Step 2: Run the tests**

Run from `demo/agent`:

```bash
python -m unittest test_ltr_ranker -v
```

Expected: fail because `ltr_ranker` does not exist.

### Task 2: Implement Linear Reranker

**Files:**
- Create: `demo/agent/ltr_ranker.py`

- [ ] **Step 1: Add dataclass and feature extraction**

Implement `LearningToRankWeights`, `rerank_scored_candidates`, and helper functions. Use only candidate fields, rule types, and optional market heatmap values.

- [ ] **Step 2: Run focused tests**

Run from `demo/agent`:

```bash
python -m unittest test_ltr_ranker -v
```

Expected: pass.

### Task 3: Runtime Integration

**Files:**
- Modify: `demo/agent/model_decision_service.py`
- Test: `demo/agent/test_decision_service.py`

- [ ] **Step 1: Add integration import and call**

Import `rerank_scored_candidates` and call it after `score_candidates`.

- [ ] **Step 2: Run full tests**

Run from `demo/agent`:

```bash
python -m unittest discover -v
```

Expected: all tests pass.

### Task 4: Replay Evaluation

**Files:**
- Create if accepted or rejected: `docs/superpowers/experiments/2026-05-15-learning-to-rank-reranker-local.md`
- Create if accepted or rejected: `docs/superpowers/experiments/2026-05-15-learning-to-rank-reranker-local.json`

- [ ] **Step 1: Run full simulator**

Run from `demo/server`:

```bash
python main.py
```

- [ ] **Step 2: Calculate monthly income**

Run from `demo`:

```bash
python calc_monthly_income.py
```

- [ ] **Step 3: Generate report**

Run from `demo/agent`:

```bash
python evaluate_results.py --results-dir ..\results --out-dir ..\..\docs\superpowers\experiments --experiment-id 2026-05-15-learning-to-rank-reranker-local --baseline ..\..\docs\superpowers\experiments\2026-05-15-hard-window-risk-scoring-local.json --timeline-driver D005 --timeline-driver D007 --timeline-driver D010
```

- [ ] **Step 4: Accept or revert**

Accept only if total net income is above 182696.6. Otherwise remove runtime integration and keep rejected report.

### Task 5: Final Verification

**Files:**
- Modified implementation files if accepted.
- Experiment report files.

- [ ] **Step 1: Run all tests**

Run from `demo/agent`:

```bash
python -m unittest discover -v
```

- [ ] **Step 2: Scan for hardcoding**

Run from repo root:

```bash
rg "D00|driver_id|cargo_id\s*==|cargo_id\s+in|司机|偏好" demo/agent --glob "!test_*.py"
```

- [ ] **Step 3: Commit and push**

Commit accepted code or rejected experiment documentation, then push branch `layered-preference-strategy`.

## Self-Review

- The plan uses tests before production code.
- The reranker has clear boundaries.
- The full replay is the acceptance gate.
