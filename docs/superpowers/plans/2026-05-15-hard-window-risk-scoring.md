# Hard Window Risk Scoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Penalize candidates that risk hard no-drive or sequence-task windows while preserving market heatmap upside.

**Architecture:** Extend `demo/agent/scoring.py` with interval-based hard-window risk helpers. Add focused tests in `demo/agent/test_scoring.py`. Run a full experiment and keep the change only if it is net-positive.

**Tech Stack:** Python standard library, unittest, existing simulation scripts.

---

### Task 1: Risk Scoring Tests

**Files:**
- Modify: `demo/agent/test_scoring.py`

- [ ] Add a test where a candidate crossing a hard no-drive window loses to a safe candidate.
- [ ] Add a test where a candidate finishing close to a hard sequence deadline loses to a safer candidate.
- [ ] Run the tests and confirm they fail before implementation.

### Task 2: Risk Penalty Implementation

**Files:**
- Modify: `demo/agent/scoring.py`

- [ ] Implement candidate current-minute derivation.
- [ ] Implement daily no-drive overlap detection.
- [ ] Implement sequence deadline buffer detection.
- [ ] Add risk reasons to scored candidates.
- [ ] Run focused and full tests.

### Task 3: Experiment Record

**Files:**
- Create: `docs/superpowers/experiments/2026-05-15-hard-window-risk-scoring-local.md`
- Create: `docs/superpowers/experiments/2026-05-15-hard-window-risk-scoring-local.json`

- [ ] Run full simulation.
- [ ] Run monthly income.
- [ ] Generate experiment delta against market heatmap scoring.
- [ ] Commit and push if the result is acceptable.
