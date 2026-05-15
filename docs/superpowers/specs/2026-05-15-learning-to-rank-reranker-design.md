# Learning-to-Rank Reranker Design

## Context

The current agent is a deterministic layered heuristic policy. It parses preferences, applies hard filters and planner intents, scores candidates, then greedily selects the highest scoring order. Full simulation currently reaches 182696.6 total net income.

The existing action logs record final decisions, not full candidate lists at each decision point. That means a fully supervised Learning-to-Rank model cannot be trained from the available logs without first adding candidate snapshot capture. A safe first experiment is therefore a small linear LTR reranker that can later be trained from snapshots, while using generic features only.

## Goal

Try a Learning-to-Rank style reranker without hardcoding driver IDs, cargo IDs, or literal preference cases. The reranker should be optional and easy to revert if full replay score drops.

## Options Considered

1. **Linear LTR reranker after current scoring**
   - Pros: small, testable, transparent, no new dependencies, can be enabled/disabled quickly.
   - Cons: initial weights are heuristic until candidate snapshots exist.

2. **Train XGBoost/LightGBM LambdaMART**
   - Pros: stronger ranking model once labels exist.
   - Cons: requires candidate snapshots and extra dependencies; risky under current time budget.

3. **Deep neural ranker / RL policy**
   - Pros: highest ceiling.
   - Cons: expensive, hard to debug, and too slow for the current iteration.

## Chosen Design

Implement option 1 as `demo/agent/ltr_ranker.py`.

The reranker will:

- consume already scored candidates,
- extract generic numeric features from each candidate,
- compute `ltr_score = base_score + weighted feature adjustments`,
- sort by `ltr_score` with stable tie-breakers,
- attach explanation strings for diagnostics.

Initial features:

- `value_per_minute`
- `rough_net_value`
- `pickup_distance_km`
- `total_order_minutes`
- `wait_minutes`
- `haul_distance_km`
- `ends_near_future_market`
- `crosses_hard_no_drive_window`
- `near_sequence_deadline`

Initial model behavior:

- slightly increase value density,
- penalize long total duration and pickup deadhead,
- preserve future market bonus,
- penalize hard-window and sequence-deadline risk.

## Safety Rules

- The reranker must not inspect driver IDs.
- The reranker must not inspect specific cargo IDs.
- Existing hard filters and planner intents remain unchanged.
- If full replay total net income is below 182696.6, revert the runtime integration and keep only experiment notes if useful.

## Test And Evaluation

- Unit tests must prove the reranker can reorder two candidates based on generic features.
- Unit tests must prove cargo IDs are only tie-breakers, not features.
- Full `python -m unittest discover -v` must pass.
- Full monthly simulation and income calculation must run.
- Experiment report compares against `2026-05-15-hard-window-risk-scoring-local`.

## Future Training Path

If the reranker infrastructure is useful, add candidate snapshot logging in a later step. Each snapshot should store candidate features, chosen action, and future realized reward. Then train LambdaMART or a regularized linear ranker offline and export weights to a small JSON file.

## Self-Review

- This spec is focused on one optional reranker.
- It has a clear accept/revert criterion.
- It avoids driver and cargo hardcoding.
