from __future__ import annotations

import unittest

from planner import build_planner_state, choose_required_intent
from preference_rules import PreferenceRule, RuleStrength, RuleType


def _rule(rule_type, value, strength=RuleStrength.HARD):
    return PreferenceRule(rule_type, strength, value, "test preference")


class PlannerTest(unittest.TestCase):
    def test_consecutive_wait_minutes_counted_from_history(self):
        history = {
            "records": [
                {"action": {"action": "wait", "params": {"duration_minutes": 20}}, "step_elapsed_minutes": 20},
                {"action": {"action": "take_order", "params": {"cargo_id": "C1"}}, "step_elapsed_minutes": 90},
                {"action": {"action": "wait", "params": {"duration_minutes": 120}}, "step_elapsed_minutes": 120},
                {"action": {"action": "wait", "params": {}}, "step_elapsed_minutes": 45},
            ]
        }

        state = build_planner_state(
            {
                "simulation_progress_minutes": 1440 + 300,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 3,
            },
            history,
        )

        self.assertEqual(state.current_minute, 1740)
        self.assertEqual(state.current_day, 2)
        self.assertEqual(state.minute_of_day, 300)
        self.assertEqual(state.current_lat, 22.54)
        self.assertEqual(state.current_lng, 114.07)
        self.assertEqual(state.completed_order_count, 3)
        self.assertEqual(state.recent_continuous_wait_minutes, 165)

    def test_daily_rest_intent_waits_when_rest_short_near_day_end(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 23 * 60,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {"records": [{"action": {"action": "wait", "params": {"duration_minutes": 90}}, "step_elapsed_minutes": 90}]},
        )
        rules = [_rule(RuleType.DAILY_REST, {"minutes": 180})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "daily_rest")
        self.assertEqual(intent.action, "wait")
        self.assertEqual(intent.params, {"duration_minutes": 90})

    def test_monthly_visit_intent_repositions_to_target(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 60,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {"records": []},
        )
        rules = [_rule(RuleType.MONTHLY_VISIT_DAYS, {"required_days": 2, "lat": 31.2304, "lng": 121.4737})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "visit_target")
        self.assertEqual(intent.action, "reposition")
        self.assertEqual(intent.params, {"latitude": 31.2304, "longitude": 121.4737})


if __name__ == "__main__":
    unittest.main()
