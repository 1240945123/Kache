"""模型决策服务：依赖 `simkit.ports.SimulationApiPort`，由评测进程注入具体环境。"""

from __future__ import annotations

import json
import logging
from typing import Any

from planner import build_planner_state, choose_required_intent
from policy_guard import filter_candidates, should_wait_for_window
from preference_parser import parse_preferences, parse_preferences_with_fallback
from preference_rules import PreferenceRule, RuleStrength, RuleType
from scoring import score_candidates
from simkit.ports import SimulationApiPort
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
        history = self._safe_history(driver_id)
        state = build_planner_state(status, history)
        deterministic_rules = [rule for rule in rules if rule.rule_type != RuleType.UNKNOWN]

        window_wait = should_wait_for_window(state.current_minute, deterministic_rules)
        if window_wait is not None:
            self._logger.info("decision required_wait driver_id=%s action=%s", driver_id, window_wait)
            return window_wait

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
        if self._has_unenforced_hard_rule(rules):
            action = fallback_wait_action()
            self._logger.info("decision unenforced_hard_rule driver_id=%s action=%s", driver_id, action)
            return action

        lat = float(status["current_lat"])
        lng = float(status["current_lng"])
        cargo_resp = self._api.query_cargo(driver_id=driver_id, latitude=lat, longitude=lng)
        items = cargo_resp.get("items", []) if isinstance(cargo_resp, dict) else []
        if not isinstance(items, list):
            return fallback_wait_action()

        candidates = filter_and_rank_candidates(items, status)
        cargo_by_id = self._cargo_by_id(items)
        allowed_candidates = filter_candidates(candidates, rules, cargo_by_id=cargo_by_id)
        allowed_candidates = self._apply_required_cargo(allowed_candidates, rules)
        if not allowed_candidates and self._required_cargo_ids(rules):
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

    def _safe_history(self, driver_id: str) -> dict[str, Any]:
        try:
            history = self._api.query_decision_history(driver_id, -1)
        except Exception as exc:
            self._logger.warning("query_decision_history failed driver_id=%s error=%s", driver_id, exc)
            return {"records": []}
        return history if isinstance(history, dict) else {"records": []}

    def _has_unenforced_hard_rule(self, rules: list[PreferenceRule]) -> bool:
        return any(rule.strength == RuleStrength.HARD and rule.rule_type in UNENFORCED_HARD_RULE_TYPES for rule in rules)

    def _required_cargo_ids(self, rules: list[PreferenceRule]) -> set[str]:
        cargo_ids: set[str] = set()
        for rule in rules:
            if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.REQUIRED_CARGO:
                continue
            cargo_id = str(rule.value.get("cargo_id", "")).strip()
            if cargo_id:
                cargo_ids.add(cargo_id)
        return cargo_ids

    def _apply_required_cargo(self, candidates: list[Candidate], rules: list[PreferenceRule]) -> list[Candidate]:
        required_cargo_ids = self._required_cargo_ids(rules)
        if not required_cargo_ids:
            return candidates
        return [candidate for candidate in candidates if candidate.cargo_id in required_cargo_ids]

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
