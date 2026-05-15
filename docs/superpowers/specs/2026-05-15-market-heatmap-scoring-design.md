# Market Heatmap Scoring Design

## Context

The current strategy has improved preference compliance, but total net income is still far below the 400000 target. Remaining penalties alone are not enough to close the gap. The next useful step is to make order selection aware of future market value instead of choosing only by current rough net value.

## Goal

Add a generic market heatmap signal that rewards cargo whose unload location leaves the truck near future cargo opportunities.

## Design

Build a lightweight `MarketHeatmap` from the public cargo dataset. It indexes cargo creation time and pickup coordinates into coarse spatial buckets. For any candidate order, the scorer estimates the future value near the candidate's unload point during a short horizon after the candidate finishes. The score becomes:

`current candidate score + future market bonus`

The bonus is capped and weighted so this first version can improve positioning without overwhelming normal profitability or hard preference rules.

## Constraints

- Do not use driver IDs, specific cargo IDs, or hand-picked routes.
- Do not change simulator data or server rules.
- Keep hard preference guards ahead of scoring.
- If the cargo dataset is unavailable in unit tests or alternate working directories, scoring must fall back to the current behavior.

## Validation

- Unit tests cover heatmap future-value lookup and scoring boost behavior.
- Full agent tests must pass.
- Full simulation must produce an experiment report against `2026-05-15-required-cargo-pursuit-local.json`.
- If total net income regresses, reduce or disable the market bonus before finalizing.
