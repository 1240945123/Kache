from __future__ import annotations

import unittest

from policy_guard import filter_candidates, is_candidate_allowed, should_wait_for_window
from preference_rules import PreferenceRule, RuleStrength, RuleType
from strategy_helpers import Candidate


def _candidate(**overrides):
    base = {
        "cargo_id": "C1",
        "price": 500.0,
        "pickup_distance_km": 10.0,
        "pickup_minutes": 10,
        "wait_minutes": 0,
        "cost_time_minutes": 120,
        "estimated_finish_minute": 200,
        "haul_distance_km": 100.0,
        "rough_net_value": 300.0,
        "value_per_minute": 2.0,
        "start": {"lat": 22.55, "lng": 114.07},
        "end": {"lat": 22.8, "lng": 114.2},
        "load_time": None,
    }
    base.update(overrides)
    return Candidate(**base)


def _rule(rule_type, strength=RuleStrength.HARD, value=None):
    return PreferenceRule(rule_type, strength, value or {}, "test preference")


class PolicyGuardTest(unittest.TestCase):
    def test_forbidden_hard_cargo_category_removes_candidate(self):
        candidate = _candidate(cargo_id="C1")
        rules = [_rule(RuleType.CARGO_CATEGORY, value={"category": "煤炭矿产"})]

        allowed = is_candidate_allowed(
            candidate,
            rules,
            cargo_by_id={"C1": {"category": "煤炭矿产"}},
        )

        self.assertFalse(allowed)

    def test_pickup_distance_limit_removes_candidate_over_limit(self):
        candidate = _candidate(pickup_distance_km=31.0)
        rules = [_rule(RuleType.PICKUP_DISTANCE_LIMIT, value={"km": 30.0})]

        self.assertFalse(is_candidate_allowed(candidate, rules, cargo_by_id={"C1": {"category": "钢材"}}))

    def test_haul_distance_limit_removes_candidate_over_limit(self):
        candidate = _candidate(haul_distance_km=301.0)
        rules = [_rule(RuleType.HAUL_DISTANCE_LIMIT, value={"km": 300.0})]

        self.assertFalse(is_candidate_allowed(candidate, rules, cargo_by_id={"C1": {"category": "钢材"}}))

    def test_no_drive_window_during_2305_returns_wait_action_duration_355(self):
        rules = [
            _rule(
                RuleType.NO_DRIVE_WINDOW,
                value={"start_minute": 1380, "end_minute": 360, "cross_day": True},
            )
        ]

        action = should_wait_for_window(1385, rules)

        self.assertEqual(action, {"action": "wait", "params": {"duration_minutes": 355}})

    def test_unknown_strong_blocks_candidates(self):
        candidates = [_candidate(cargo_id="C1"), _candidate(cargo_id="C2")]
        rules = [_rule(RuleType.UNKNOWN, strength=RuleStrength.UNKNOWN_STRONG)]

        self.assertEqual(filter_candidates(candidates, rules, cargo_by_id={}), [])


if __name__ == "__main__":
    unittest.main()
