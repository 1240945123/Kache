from __future__ import annotations

import unittest

from planner import build_planner_state, choose_required_intent
from preference_rules import PreferenceRule, RuleStrength, RuleType


def _rule(rule_type, value, strength=RuleStrength.HARD):
    return PreferenceRule(rule_type, strength, value, "test preference")


class PlannerTest(unittest.TestCase):
    def _sequence_rule(self):
        return _rule(
            RuleType.SEQUENCE_TASK,
            {
                "steps": [
                    {"action": "pickup", "lat": 23.21, "lng": 113.37, "wait_minutes": 10},
                    {"action": "return_home", "lat": 23.19, "lng": 113.36},
                ],
                "deadline": "2026-03-10 22:00:00",
                "stay_until": "2026-03-13 22:00:00",
            },
        )

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

    def test_monthly_visit_intent_is_none_when_enough_distinct_visit_days_satisfied(self):
        history = {
            "records": [
                {
                    "action": {"action": "reposition", "params": {"latitude": 31.2304, "longitude": 121.4737}},
                    "position_after": {"lat": 31.2304, "lng": 121.4737},
                    "simulation_end_time": "2026-03-01 05:00",
                    "step_elapsed_minutes": 60,
                },
                {
                    "action": {"action": "wait", "params": {"duration_minutes": 30}},
                    "position_after": {"lat": 31.2310, "lng": 121.4740},
                    "simulation_end_time": "2026-03-02 01:00",
                    "step_elapsed_minutes": 30,
                },
            ]
        }
        state = build_planner_state(
            {
                "simulation_progress_minutes": 1440 + 60,
                "current_lat": 31.2310,
                "current_lng": 121.4740,
                "completed_order_count": 0,
            },
            history,
        )
        rules = [_rule(RuleType.MONTHLY_VISIT_DAYS, {"required_days": 2, "lat": 31.2304, "lng": 121.4737, "radius_km": 1.0})]

        self.assertIsNone(choose_required_intent(state, rules))

    def test_monthly_visit_intent_still_occurs_after_required_day_count_if_not_satisfied(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 4 * 1440,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "reposition", "params": {"latitude": 31.2304, "longitude": 121.4737}},
                        "position_after": {"lat": 31.2304, "lng": 121.4737},
                        "simulation_end_time": "2026-03-01 05:00",
                        "step_elapsed_minutes": 60,
                    }
                ]
            },
        )
        rules = [_rule(RuleType.MONTHLY_VISIT_DAYS, {"required_days": 2, "lat": 31.2304, "lng": 121.4737, "radius_km": 1.0})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "visit_target")
        self.assertEqual(intent.action, "reposition")

    def test_monthly_visit_waits_once_when_already_at_target_on_new_day(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 1440 + 60,
                "current_lat": 31.2304,
                "current_lng": 121.4737,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "reposition", "params": {"latitude": 31.2304, "longitude": 121.4737}},
                        "position_after": {"lat": 31.2304, "lng": 121.4737},
                        "simulation_end_time": "2026-03-01 05:00",
                    }
                ]
            },
        )
        rules = [_rule(RuleType.MONTHLY_VISIT_DAYS, {"required_days": 2, "lat": 31.2304, "lng": 121.4737, "radius_km": 1.0})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "visit_target_wait")
        self.assertEqual(intent.action, "wait")

    def test_monthly_visit_does_not_repeat_reposition_after_current_day_credit(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 1440 + 120,
                "current_lat": 31.2304,
                "current_lng": 121.4737,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "wait", "params": {"duration_minutes": 30}},
                        "position_after": {"lat": 31.2304, "lng": 121.4737},
                        "simulation_end_time": "2026-03-02 01:30",
                    }
                ]
            },
        )
        rules = [_rule(RuleType.MONTHLY_VISIT_DAYS, {"required_days": 5, "lat": 31.2304, "lng": 121.4737, "radius_km": 1.0})]

        self.assertIsNone(choose_required_intent(state, rules))

    def test_monthly_no_order_day_waits_at_start_of_month(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 8 * 60,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {"records": []},
        )
        rules = [_rule(RuleType.MONTHLY_NO_ORDER_DAYS, {"required_days": 1})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "monthly_no_order_day")
        self.assertEqual(intent.action, "wait")

    def test_daily_order_limit_waits_after_limit_reached(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 12 * 60,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 2,
            },
            {
                "records": [
                    {"action": {"action": "take_order"}, "result": {"accepted": True}, "simulation_end_time": "2026-03-01 09:00"},
                    {"action": {"action": "take_order"}, "result": {"accepted": True}, "simulation_end_time": "2026-03-01 11:00"},
                ]
            },
        )
        rules = [_rule(RuleType.DAILY_ORDER_LIMIT, {"max_orders": 2})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "daily_order_limit")
        self.assertEqual(intent.action, "wait")

    def test_first_order_deadline_waits_after_missing_deadline(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 13 * 60,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {"records": []},
        )
        rules = [_rule(RuleType.FIRST_ORDER_DEADLINE, {"deadline_minute": 12 * 60})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "first_order_deadline")
        self.assertEqual(intent.action, "wait")

    def test_home_deadline_repositions_home_after_deadline(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 23 * 60 + 10,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {"records": []},
        )
        rules = [_rule(RuleType.HOME_DEADLINE, {"deadline_minute": 23 * 60, "lat": 23.12, "lng": 113.28, "radius_km": 1.0})]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "home_deadline")
        self.assertEqual(intent.action, "reposition")
        self.assertEqual(intent.params, {"latitude": 23.12, "longitude": 113.28})

    def test_sequence_task_repositions_to_first_step_before_deadline(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 9 * 24 * 60 + 10 * 60,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {"records": []},
        )
        rules = [
            _rule(
                RuleType.SEQUENCE_TASK,
                {
                    "steps": [
                        {"action": "pickup", "lat": 23.21, "lng": 113.37, "wait_minutes": 10},
                        {"action": "return_home", "lat": 23.19, "lng": 113.36},
                    ],
                    "deadline": "2026-03-10 22:00:00",
                    "stay_until": "2026-03-13 22:00:00",
                },
            )
        ]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "sequence_pickup")
        self.assertEqual(intent.action, "reposition")
        self.assertEqual(intent.params, {"latitude": 23.21, "longitude": 113.37})

    def test_sequence_task_stays_home_during_stay_window(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 10 * 24 * 60 + 23 * 60,
                "current_lat": 23.19,
                "current_lng": 113.36,
                "completed_order_count": 0,
            },
            {"records": []},
        )
        rules = [
            _rule(
                RuleType.SEQUENCE_TASK,
                {
                    "steps": [
                        {"action": "pickup", "lat": 23.21, "lng": 113.37, "wait_minutes": 10},
                        {"action": "return_home", "lat": 23.19, "lng": 113.36},
                    ],
                    "deadline": "2026-03-10 22:00:00",
                    "stay_until": "2026-03-13 22:00:00",
                },
            )
        ]

        intent = choose_required_intent(state, rules)

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "sequence_stay_home")
        self.assertEqual(intent.action, "wait")

    def test_sequence_task_waits_remaining_pickup_dwell_when_at_pickup(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60,
                "current_lat": 23.21,
                "current_lng": 113.37,
                "completed_order_count": 0,
            },
            {"records": []},
        )

        intent = choose_required_intent(state, [self._sequence_rule()])

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "sequence_pickup_wait")
        self.assertEqual(intent.action, "wait")
        self.assertEqual(intent.params, {"duration_minutes": 10})

    def test_sequence_task_waits_only_remaining_pickup_dwell(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60 + 4,
                "current_lat": 23.21,
                "current_lng": 113.37,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "wait", "params": {"duration_minutes": 4}},
                        "position_after": {"lat": 23.21, "lng": 113.37},
                        "simulation_end_time": "2026-03-10 16:04",
                        "step_elapsed_minutes": 4,
                    }
                ]
            },
        )

        intent = choose_required_intent(state, [self._sequence_rule()])

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "sequence_pickup_wait")
        self.assertEqual(intent.params, {"duration_minutes": 6})

    def test_sequence_task_returns_home_after_pickup_dwell_satisfied(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60 + 10,
                "current_lat": 23.21,
                "current_lng": 113.37,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "wait", "params": {"duration_minutes": 10}},
                        "position_after": {"lat": 23.21, "lng": 113.37},
                        "simulation_end_time": "2026-03-10 16:10",
                        "step_elapsed_minutes": 10,
                    }
                ]
            },
        )

        intent = choose_required_intent(state, [self._sequence_rule()])

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "sequence_return_home")
        self.assertEqual(intent.action, "reposition")
        self.assertEqual(intent.params, {"latitude": 23.19, "longitude": 113.36})

    def test_sequence_task_remembers_pickup_dwell_after_returning_home(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60 + 16,
                "current_lat": 23.19,
                "current_lng": 113.36,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "wait", "params": {"duration_minutes": 10}},
                        "position_after": {"lat": 23.21, "lng": 113.37},
                        "simulation_end_time": "2026-03-10 16:10",
                        "step_elapsed_minutes": 10,
                    },
                    {
                        "action": {"action": "reposition", "params": {"latitude": 23.19, "longitude": 113.36}},
                        "position_after": {"lat": 23.19, "lng": 113.36},
                        "simulation_end_time": "2026-03-10 16:16",
                        "step_elapsed_minutes": 6,
                    },
                ]
            },
        )

        intent = choose_required_intent(state, [self._sequence_rule()])

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "sequence_stay_home")
        self.assertEqual(intent.action, "wait")

    def test_sequence_task_stays_home_until_stay_until_after_pickup_dwell(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60 + 10,
                "current_lat": 23.19,
                "current_lng": 113.36,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "wait", "params": {"duration_minutes": 10}},
                        "position_after": {"lat": 23.21, "lng": 113.37},
                        "simulation_end_time": "2026-03-10 16:10",
                        "step_elapsed_minutes": 10,
                    }
                ]
            },
        )

        intent = choose_required_intent(state, [self._sequence_rule()])

        self.assertIsNotNone(intent)
        self.assertEqual(intent.intent_type, "sequence_stay_home")
        self.assertEqual(intent.action, "wait")
        self.assertEqual(intent.params, {"duration_minutes": (12 * 24 * 60 + 22 * 60) - state.current_minute})

    def test_current_day_rest_credit_clips_wait_that_crossed_midnight(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 1440 + 30,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {
                        "action": {"action": "wait", "params": {"duration_minutes": 90}},
                        "step_elapsed_minutes": 90,
                    }
                ]
            },
        )

        self.assertEqual(state.recent_continuous_wait_minutes, 30)

    def test_malformed_and_negative_wait_durations_do_not_crash_or_reduce_rest_credit(self):
        state = build_planner_state(
            {
                "simulation_progress_minutes": 180,
                "current_lat": 22.54,
                "current_lng": 114.07,
                "completed_order_count": 0,
            },
            {
                "records": [
                    {"action": {"action": "wait", "params": {"duration_minutes": 60}}, "step_elapsed_minutes": 60},
                    {"action": {"action": "wait", "params": {"duration_minutes": -30}}, "step_elapsed_minutes": -30},
                    {"action": {"action": "wait", "params": {"duration_minutes": "bad"}}, "step_elapsed_minutes": "bad"},
                ]
            },
        )

        self.assertEqual(state.recent_continuous_wait_minutes, 60)


if __name__ == "__main__":
    unittest.main()
