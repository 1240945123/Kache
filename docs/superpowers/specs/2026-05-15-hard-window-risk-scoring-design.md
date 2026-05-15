# Hard Window Risk Scoring Design

## Context

Market heatmap scoring increased total net income, but it also raised preference penalties for drivers with time-sensitive rules. The next optimization should keep the market signal while reducing orders that run through hard no-drive windows or consume time close to hard sequence-task deadlines.

## Goal

Add a generic hard-window risk penalty to candidate scoring.

## Design

The scorer will estimate the candidate execution interval from the current minute to the candidate finish minute. For hard `NO_DRIVE_WINDOW` rules, if that interval intersects the daily blocked window, the candidate receives a risk penalty. For hard `SEQUENCE_TASK` rules, if the candidate would finish inside a conservative buffer before the parsed deadline, it receives a risk penalty so the planner can take over earlier.

This is a scoring penalty, not a hard filter. That matters because some orders may still be worth taking when no safe alternative exists.

## Constraints

- No driver ID, cargo ID, or data-row hardcoding.
- Required-cargo and existing hard guards remain in front of ordinary scoring.
- Penalty values should be large enough to offset the heatmap bonus but not so large that all revenue collapses.

## Validation

- Unit tests prove no-drive overlap and sequence deadline risk can change ranking.
- Full simulation compares against `2026-05-15-market-heatmap-scoring-local.json`.
- If total net income regresses sharply, reduce risk penalties and rerun.
