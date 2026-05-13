# KACHE Project Overview

## Purpose

This repository contains a Tianchi Agent competition package for a truck-driver cargo matching simulation. The goal is to implement a decision-making Agent that repeatedly chooses one action per step for each driver over a simulated month:

- `take_order`: accept a visible cargo order
- `wait`: rest in place for a positive number of minutes
- `reposition`: deadhead to a target coordinate

The scoring objective is long-term monthly net income after distance costs and driver preference penalties.

## Top-Level Contents

- `docs/`: Chinese competition documentation, data rules, scoring rules, submission format, quick start, and changelog.
- `demo/`: runnable local evaluation package.
- `demo_docs_release_20260508.zip`: release archive for the docs/demo package.

## Demo Layout

- `demo/agent/model_decision_service.py`: primary competitor decision implementation. It receives a `SimulationApiPort`, queries state/cargo, calls a model, parses one JSON action, and returns it.
- `demo/simkit/ports.py`: protocol boundary between agent and simulator.
- `demo/simkit/cargo_repository.py`: in-memory cargo lifecycle and nearest-cargo lookup.
- `demo/simkit/driver_state_manager.py`: in-memory driver state and simulation clock.
- `demo/simkit/simulation_actions.py`: shared action semantics for distance, cargo query scan cost, order execution, wait, and reposition.
- `demo/server/main.py`: local simulation entry point.
- `demo/server/bench/`: evaluation orchestration, embedded agent environment, settings, and model gateway.
- `demo/server/config/config.example.json`: example local evaluation config.
- `demo/server/data/`: sample cargo and driver data for local evaluation only.
- `demo/calc_monthly_income.py`: local income, legality, token, and preference validation script.

## Data And Rule Constraints

- Decision code must not directly open or scan `demo/server/data/cargo_dataset.jsonl` or `demo/server/data/drivers.json`.
- Agent-visible state must come through `SimulationApiPort`:
  - `get_driver_status(driver_id)`
  - `query_cargo(driver_id, latitude, longitude)`
  - `query_decision_history(driver_id, step)`
  - `model_chat_completion(payload)`
- `query_cargo` advances simulation time according to returned item count and configured batch size.
- `take_order` includes pickup deadhead, possible load-window waiting, and cargo transport time.
- `wait` advances time without moving.
- `reposition` advances time and cost according to Haversine distance and configured speed.

## Evaluation Flow

1. `demo/server/main.py` loads config, cargo data, drivers, and the embedded agent.
2. `SimulationOrchestrator` loops through drivers, resetting each driver and cargo repository for that driver's simulation.
3. Each step calls `ModelDecisionService.decide(driver_id)`.
4. The simulator applies the returned action and writes per-driver action logs.
5. `demo/calc_monthly_income.py` validates action logs and computes final income and preference penalties.

## High-Leverage Development Areas

- Improve `demo/agent/model_decision_service.py` so it plans across time instead of making a single-step nearest-cargo choice.
- Use `get_driver_status` preferences and `query_decision_history` to track driver-specific constraints and prior behavior.
- Add deterministic fallback logic around model outputs so malformed or risky decisions do not crash or waste steps.
- Score candidate cargo by expected net value, pickup distance, load window feasibility, finish time, truck length, and visible driver preferences.
- Add small local tests for pure helper functions before embedding strategy changes into `ModelDecisionService`.

## Superpowers Usage In This Project

- Use `brainstorming` for strategy design and scoring tradeoffs.
- Use `writing-plans` before multi-step agent improvements.
- Use `test-driven-development` for helper functions and policy rules.
- Use `systematic-debugging` for failed simulations, validation errors, bad income, or stuck loops.
- Use `verification-before-completion` before considering a submission-ready change complete.
