from __future__ import annotations

import unittest

from strategy_helpers import (
    DEFAULT_FALLBACK_WAIT_MINUTES,
    build_candidate,
    fallback_wait_action,
    filter_and_rank_candidates,
    parse_model_action,
    take_top_candidate_action,
)


def _status(**overrides):
    base = {
        "current_lat": 22.54,
        "current_lng": 114.06,
        "truck_length": "4.2米",
        "simulation_progress_minutes": 60,
    }
    base.update(overrides)
    return base


def _item(**cargo_overrides):
    cargo = {
        "cargo_id": "C1",
        "remove_time": "2026-03-01 23:59:59",
        "price": 500.0,
        "cost_time_minutes": 120,
        "load_time": ["2026-03-01 02:00:00", "2026-03-01 06:00:00"],
        "truck_length": ["4.2米"],
        "start": {"lat": 22.55, "lng": 114.07},
        "end": {"lat": 22.8, "lng": 114.2},
    }
    cargo.update(cargo_overrides)
    return {"distance_km": 1.5, "cargo": cargo}


class StrategyHelpersTest(unittest.TestCase):
    def test_build_candidate_accepts_valid_positive_candidate(self):
        candidate = build_candidate(_item(), _status())
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.cargo_id, "C1")
        self.assertGreater(candidate.rough_net_value, 0)
        self.assertGreater(candidate.estimated_finish_minute, 60)

    def test_expired_load_window_is_filtered(self):
        expired = _item(load_time=["2026-03-01 00:00:00", "2026-03-01 00:30:00"])
        ranked = filter_and_rank_candidates([expired], _status(simulation_progress_minutes=120))
        self.assertEqual(ranked, [])

    def test_removed_cargo_is_filtered_when_pickup_arrives_after_remove_time(self):
        removed = _item(remove_time="2026-03-01 00:30:00")
        ranked = filter_and_rank_candidates([removed], _status(simulation_progress_minutes=33))
        self.assertEqual(ranked, [])

    def test_negative_value_candidate_is_filtered(self):
        bad = _item(price=1.0)
        ranked = filter_and_rank_candidates([bad], _status())
        self.assertEqual(ranked, [])

    def test_missing_coordinates_candidate_is_skipped(self):
        malformed = _item(start={})
        ranked = filter_and_rank_candidates([malformed], _status())
        self.assertEqual(ranked, [])

    def test_unsupported_truck_length_is_filtered(self):
        wrong_truck = _item(truck_length=["13.0米"])
        ranked = filter_and_rank_candidates([wrong_truck], _status(truck_length="4.2米"))
        self.assertEqual(ranked, [])

    def test_candidate_beyond_horizon_is_filtered(self):
        late = _item(cost_time_minutes=240)
        ranked = filter_and_rank_candidates([late], _status(simulation_progress_minutes=1300), horizon_minutes=1440)
        self.assertEqual(ranked, [])

    def test_candidates_rank_by_rough_value(self):
        low = _item(cargo_id="LOW", price=300.0)
        high = _item(cargo_id="HIGH", price=800.0)
        ranked = filter_and_rank_candidates([low, high], _status())
        self.assertEqual([c.cargo_id for c in ranked], ["HIGH", "LOW"])

    def test_parse_model_action_rejects_unapproved_cargo(self):
        response = {"choices": [{"message": {"content": "{\"action\":\"take_order\",\"params\":{\"cargo_id\":\"BAD\"}}"}}]}
        action = parse_model_action(response, allowed_cargo_ids={"GOOD"})
        self.assertEqual(action, fallback_wait_action())

    def test_fallback_wait_action_is_valid(self):
        self.assertEqual(
            fallback_wait_action(),
            {"action": "wait", "params": {"duration_minutes": DEFAULT_FALLBACK_WAIT_MINUTES}},
        )

    def test_take_top_candidate_action_uses_best_ranked_candidate(self):
        low = _item(cargo_id="LOW", price=300.0)
        high = _item(cargo_id="HIGH", price=800.0)
        ranked = filter_and_rank_candidates([low, high], _status())
        self.assertEqual(take_top_candidate_action(ranked), {"action": "take_order", "params": {"cargo_id": "HIGH"}})


if __name__ == "__main__":
    unittest.main()
