# Market Heatmap Scoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generic future-market-value bonus to cargo scoring.

**Architecture:** Create `demo/agent/market_heatmap.py` as a small read-only market model. Extend `demo/agent/scoring.py` to accept an optional heatmap and include a capped future-value bonus. Wire `model_decision_service.py` to load the heatmap from the local cargo dataset when available.

**Tech Stack:** Python standard library, existing unittest suite, existing local simulation scripts.

---

### Task 1: Heatmap Model

**Files:**
- Create: `demo/agent/market_heatmap.py`
- Create: `demo/agent/test_market_heatmap.py`

- [ ] Write tests for future cargo near a coordinate, ignoring past cargo, and bounded scores.
- [ ] Implement `MarketHeatmap.from_cargo_records`, `future_value`, and `load_default_market_heatmap`.
- [ ] Run `python -m unittest test_market_heatmap.py -v` from `demo/agent`.
- [ ] Commit.

### Task 2: Scoring Integration

**Files:**
- Modify: `demo/agent/scoring.py`
- Modify: `demo/agent/test_scoring.py`

- [ ] Write a failing test showing a lower immediate-value candidate can outrank another when it ends in a high-value future market.
- [ ] Add optional `market_heatmap` to `score_candidate` and `score_candidates`.
- [ ] Add reasons for future market bonus.
- [ ] Run `python -m unittest test_scoring.py test_market_heatmap.py -v` from `demo/agent`.
- [ ] Commit.

### Task 3: Decision Wiring And Experiment

**Files:**
- Modify: `demo/agent/model_decision_service.py`
- Create: `docs/superpowers/experiments/2026-05-15-market-heatmap-scoring-local.md`
- Create: `docs/superpowers/experiments/2026-05-15-market-heatmap-scoring-local.json`

- [ ] Load the default heatmap once and pass it to `score_candidates`.
- [ ] Run full unit tests and hardcoding scan.
- [ ] Run full simulation, monthly income, and experiment report.
- [ ] If score regresses, lower the heatmap weight and rerun.
- [ ] Commit and push the final result.
