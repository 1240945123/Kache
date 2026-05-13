# Superpowers Project Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make this project consistently start from the Superpowers workflow and give future agents a compact, accurate map of the repository.

**Architecture:** Store project-level behavior in `AGENTS.md`, keep durable project understanding in `docs/superpowers/project-overview.md`, and use this plan as the handoff for deeper implementation work. No runtime code changes are required for onboarding.

**Tech Stack:** Codex project instructions, Markdown documentation, Python simulation package.

---

## File Structure

- Create: `AGENTS.md`
  - Project-level Codex instructions that tell future agents to use Superpowers and preserve competition constraints.
- Create: `docs/superpowers/project-overview.md`
  - A concise repository map, evaluation flow, data constraints, and development priorities.
- Create: `docs/superpowers/plans/2026-05-09-superpowers-project-onboarding.md`
  - This implementation and handoff plan.

### Task 1: Add Project-Level Superpowers Instructions

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Write the project instruction file**

Create `AGENTS.md` with these sections:

```markdown
# Project Codex Instructions

## Superpowers

- For this project, always begin substantial work by using the installed Superpowers workflow.
- Before planning, implementing, debugging, reviewing, or preparing a submission, read the relevant Superpowers skill first.
- Default sequence:
  - Use `using-superpowers` as the entry point.
  - Use `brainstorming` when requirements are unclear or strategy choices matter.
  - Use `writing-plans` before multi-step code changes.
  - Use `test-driven-development` when changing decision logic or scoring behavior.
  - Use `systematic-debugging` for failed simulations, validation errors, or unexpected income results.
  - Use `verification-before-completion` before declaring work complete.
```

- [ ] **Step 2: Verify the file exists**

Run:

```powershell
Test-Path AGENTS.md
```

Expected: `True`

### Task 2: Record The Repository Map

**Files:**
- Create: `docs/superpowers/project-overview.md`

- [ ] **Step 1: Write the project overview**

Create `docs/superpowers/project-overview.md` with:

```markdown
# KACHE Project Overview

## Purpose

This repository contains a Tianchi Agent competition package for a truck-driver cargo matching simulation.

## Demo Layout

- `demo/agent/model_decision_service.py`: primary competitor decision implementation.
- `demo/simkit/ports.py`: protocol boundary between agent and simulator.
- `demo/simkit/simulation_actions.py`: shared action semantics.
- `demo/server/main.py`: local simulation entry point.
- `demo/calc_monthly_income.py`: local income and legality validation script.
```

- [ ] **Step 2: Verify the overview has the required headings**

Run:

```powershell
Select-String -Path docs\superpowers\project-overview.md -Pattern "Purpose","Demo Layout","Evaluation Flow","Superpowers Usage"
```

Expected: one match for each pattern.

### Task 3: Use The Overview For Next Development Planning

**Files:**
- Modify: `demo/agent/model_decision_service.py`
- Test: future focused tests under a new test location, if the project adopts tests

- [ ] **Step 1: Choose a first agent improvement target**

Pick one of these scoped improvements:

```text
1. Add deterministic candidate scoring before model selection.
2. Add preference-aware prompt context.
3. Add robust fallback actions when model JSON is invalid or risky.
4. Add history-aware rest and reposition strategy.
```

- [ ] **Step 2: Write a dedicated implementation plan**

Run a new Superpowers planning pass and save it as:

```text
docs/superpowers/plans/YYYY-MM-DD-agent-strategy-improvement.md
```

Expected: the plan lists exact helper functions, tests, commands, and verification steps.

## Self-Review

- Spec coverage: the user's request asked to read and plan the project contents and enable project-level Superpowers triggering. This plan covers project instructions, project map, and future development planning.
- Placeholder scan: no `TBD`, `TODO`, or unspecified implementation step remains.
- Type consistency: no code symbols are introduced here beyond existing project files and documented paths.
