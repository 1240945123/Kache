"""模型决策服务：依赖 `simkit.ports.SimulationApiPort`，由评测进程注入具体环境。"""

from __future__ import annotations

import json
import logging
from typing import Any

from simkit.ports import SimulationApiPort

if __package__:
    from .planner import build_planner_state, choose_required_intent
    from .policy_guard import filter_candidates, should_wait_for_window
    from .preference_parser import parse_preferences, parse_preferences_with_fallback
    from .preference_rules import PreferenceRule, RuleStrength, RuleType
    from .scoring import score_candidates
    from .strategy_helpers import Candidate
    from .strategy_helpers import fallback_wait_action, filter_and_rank_candidates
else:
    from planner import build_planner_state, choose_required_intent
    from policy_guard import filter_candidates, should_wait_for_window
    from preference_parser import parse_preferences, parse_preferences_with_fallback
    from preference_rules import PreferenceRule, RuleStrength, RuleType
    from scoring import score_candidates
    from strategy_helpers import Candidate
    from strategy_helpers import fallback_wait_action, filter_and_rank_candidates

UNENFORCED_HARD_RULE_TYPES = {
    RuleType.BOUNDING_BOX,
    RuleType.FORBIDDEN_ZONE,
    RuleType.HOME_DEADLINE,
    RuleType.MONTHLY_DEADHEAD_LIMIT,
    RuleType.MONTHLY_NO_ORDER_DAYS,
    RuleType.MONTHLY_OFF_DAYS,
    RuleType.SEQUENCE_TASK,
    RuleType.STAY_WINDOW,
}


class ModelDecisionService:
    """Layered deterministic strategy with model fallback only for unknown strong preferences."""

    def __init__(self, api: SimulationApiPort) -> None:
        self._api = api
        self._logger = logging.getLogger("agent.decision_service")

    def decide(self, driver_id: str) -> dict[str, Any]:
        status = self._api.get_driver_status(driver_id)
        preferences = status.get("preferences", [])
        rules = parse_preferences(preferences)
        unknown_strong_sources = self._unknown_strong_sources(rules)
        deterministic_rules = [rule for rule in rules if rule.rule_type != RuleType.UNKNOWN]

        current_minute = int(status.get("simulation_progress_minutes", 0) or 0)
        window_wait = should_wait_for_window(current_minute, deterministic_rules)
        if window_wait is not None:
            self._logger.info("decision required_wait driver_id=%s action=%s", driver_id, window_wait)
            return window_wait

        history: dict[str, Any] | None = None
        history_step = self._history_step_for_planner(deterministic_rules)
        if history_step is not None:
            history = self._safe_history(driver_id, history_step)
            state = build_planner_state(status, history)
            intent = choose_required_intent(state, deterministic_rules)
            if intent is not None:
                action = {"action": intent.action, "params": intent.params}
                self._logger.info(
                    "decision planner_intent driver_id=%s intent=%s action=%s",
                    driver_id,
                    intent.intent_type,
                    action,
                )
                return action

        rules = parse_preferences_with_fallback(
            preferences,
            model_parse_fn=self._model_parse_preference,
            max_model_calls=1,
        )
        if self._has_unenforced_fallback_rule(rules, unknown_strong_sources):
            action = fallback_wait_action()
            self._logger.info("decision unenforced_fallback_rule driver_id=%s action=%s", driver_id, action)
            return action

        lat = float(status["current_lat"])
        lng = float(status["current_lng"])
        cargo_resp = self._api.query_cargo(driver_id=driver_id, latitude=lat, longitude=lng)
        items = cargo_resp.get("items", []) if isinstance(cargo_resp, dict) else []
        if not isinstance(items, list):
            return fallback_wait_action()

        cargo_by_id = self._cargo_by_id(items)
        required_cargo_ids = self._required_cargo_ids(rules)
        candidate_limit = len(items) if required_cargo_ids else 10
        candidates = filter_and_rank_candidates(
            items,
            status,
            limit=candidate_limit,
            max_total_order_minutes=None if required_cargo_ids else 12 * 60,
        )
        allowed_candidates = filter_candidates(candidates, rules, cargo_by_id=cargo_by_id)
        if self._has_monthly_deadhead_limit(rules):
            if history is None:
                history = self._safe_history(driver_id, -1)
            allowed_candidates = self._apply_monthly_deadhead_limit(allowed_candidates, rules, history)
        allowed_candidates = self._apply_required_cargo(allowed_candidates, required_cargo_ids)
        if not allowed_candidates and required_cargo_ids:
            action = fallback_wait_action()
            self._logger.info("decision required_cargo_missing driver_id=%s action=%s", driver_id, action)
            return action
        scored_candidates = score_candidates(allowed_candidates, rules, cargo_by_id=cargo_by_id)

        if scored_candidates:
            chosen = scored_candidates[0].candidate
            action = {"action": "take_order", "params": {"cargo_id": chosen.cargo_id}}
            self._logger.info(
                "decision scored_take_order driver_id=%s cargo_id=%s score=%.3f",
                driver_id,
                chosen.cargo_id,
                scored_candidates[0].score,
            )
            return action

        action = fallback_wait_action()
        self._logger.info("decision fallback_wait driver_id=%s action=%s", driver_id, action)
        return action

    def _history_step_for_planner(self, rules: list[PreferenceRule]) -> int | None:
        needs_daily_rest = False
        history_rule_types = {
            RuleType.DAILY_ORDER_LIMIT,
            RuleType.FIRST_ORDER_DEADLINE,
            RuleType.HOME_DEADLINE,
            RuleType.MONTHLY_DEADHEAD_LIMIT,
            RuleType.MONTHLY_NO_ORDER_DAYS,
            RuleType.MONTHLY_OFF_DAYS,
            RuleType.MONTHLY_VISIT_DAYS,
            RuleType.REQUIRED_CARGO,
            RuleType.SEQUENCE_TASK,
        }
        for rule in rules:
            if rule.strength != RuleStrength.HARD:
                continue
            if rule.rule_type in history_rule_types:
                return -1
            if rule.rule_type == RuleType.DAILY_REST:
                needs_daily_rest = True
        return 100 if needs_daily_rest else None

    def _safe_history(self, driver_id: str, step: int) -> dict[str, Any]:
        try:
            history = self._api.query_decision_history(driver_id, step)
        except Exception as exc:
            self._logger.warning("query_decision_history failed driver_id=%s error=%s", driver_id, exc)
            return {"records": []}
        return history if isinstance(history, dict) else {"records": []}

    def _unknown_strong_sources(self, rules: list[PreferenceRule]) -> set[str]:
        return {
            rule.source_text
            for rule in rules
            if rule.rule_type == RuleType.UNKNOWN and rule.strength == RuleStrength.UNKNOWN_STRONG
        }

    def _has_unenforced_fallback_rule(self, rules: list[PreferenceRule], unknown_strong_sources: set[str]) -> bool:
        for rule in rules:
            if rule.source_text not in unknown_strong_sources:
                continue
            if rule.strength == RuleStrength.UNKNOWN_STRONG:
                return True
            if rule.strength == RuleStrength.HARD and rule.rule_type in UNENFORCED_HARD_RULE_TYPES:
                return True
        return False

    def _required_cargo_ids(self, rules: list[PreferenceRule]) -> set[str]:
        cargo_ids: set[str] = set()
        for rule in rules:
            if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.REQUIRED_CARGO:
                continue
            cargo_id = str(rule.value.get("cargo_id", "")).strip()
            if cargo_id:
                cargo_ids.add(cargo_id)
        return cargo_ids

    def _apply_required_cargo(self, candidates: list[Candidate], required_cargo_ids: set[str]) -> list[Candidate]:
        if not required_cargo_ids:
            return candidates
        return [candidate for candidate in candidates if candidate.cargo_id in required_cargo_ids]

    def _has_monthly_deadhead_limit(self, rules: list[PreferenceRule]) -> bool:
        return any(rule.strength == RuleStrength.HARD and rule.rule_type == RuleType.MONTHLY_DEADHEAD_LIMIT for rule in rules)

    def _monthly_deadhead_used_km(self, history: dict[str, Any]) -> float:
        records = history.get("records", []) if isinstance(history, dict) else []
        total = 0.0
        if not isinstance(records, list):
            return total
        for record in records:
            if not isinstance(record, dict):
                continue
            result = record.get("result")
            if not isinstance(result, dict):
                continue
            try:
                total += max(0.0, float(result.get("pickup_deadhead_km", 0.0) or 0.0))
            except (TypeError, ValueError):
                continue
        return total

    def _apply_monthly_deadhead_limit(
        self,
        candidates: list[Candidate],
        rules: list[PreferenceRule],
        history: dict[str, Any],
    ) -> list[Candidate]:
        limits: list[float] = []
        for rule in rules:
            if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.MONTHLY_DEADHEAD_LIMIT:
                continue
            try:
                limits.append(float(rule.value["km"]))
            except (KeyError, TypeError, ValueError):
                continue
        if not limits:
            return candidates
        remaining_km = min(limits) - self._monthly_deadhead_used_km(history)
        return [candidate for candidate in candidates if candidate.pickup_distance_km <= remaining_km]

    def _model_parse_preference(self, text: str) -> dict[str, Any]:
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "把货运司机偏好文本转成JSON。只输出JSON对象，格式为"
                        "{\"rules\":[{\"rule_type\":\"stay_window\",\"strength\":\"hard\","
                        "\"value\":{},\"source_text\":\"...\"}]}。"
                        "rule_type只能使用preference_rules.RuleType中的字符串值。"
                    ),
                },
                {"role": "user", "content": str(text or "")},
            ],
            "response_format": {"type": "json_object"},
        }
        response = self._api.model_chat_completion(payload)
        choices = response.get("choices", []) if isinstance(response, dict) else []
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else {"rules": []}

    def _cargo_by_id(self, items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        cargo_by_id: dict[str, dict[str, Any]] = {}
        for item in items:
            cargo = item.get("cargo") if isinstance(item, dict) else None
            if not isinstance(cargo, dict):
                continue
            cargo_id = str(cargo.get("cargo_id", "")).strip()
            if cargo_id:
                cargo_by_id[cargo_id] = cargo
        return cargo_by_id
