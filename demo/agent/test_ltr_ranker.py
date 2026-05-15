from __future__ import annotations

import unittest

from preference_rules import PreferenceRule, RuleStrength, RuleType
from scoring import ScoredCandidate
from strategy_helpers import Candidate
from ltr_ranker import LearningToRankWeights, rerank_scored_candidates


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


class LearningToRankRerankerTest(unittest.TestCase):
    def test_value_density_can_rerank_close_base_scores(self):
        slow_high_base = ScoredCandidate(
            _candidate(cargo_id="SLOW", rough_net_value=320.0, value_per_minute=1.0, cost_time_minutes=300),
            320.0,
            ["base"],
        )
        dense_lower_base = ScoredCandidate(
            _candidate(cargo_id="DENSE", rough_net_value=300.0, value_per_minute=10.0, cost_time_minutes=40),
            300.0,
            ["base"],
        )
        weights = LearningToRankWeights(value_per_minute=4.0, total_order_minutes=-0.01)

        reranked = rerank_scored_candidates([slow_high_base, dense_lower_base], [], weights=weights)

        self.assertEqual([item.candidate.cargo_id for item in reranked], ["DENSE", "SLOW"])
        self.assertTrue(any("ltr adjustment" in reason for reason in reranked[0].reasons))

    def test_cargo_id_is_only_a_tie_breaker(self):
        second = ScoredCandidate(_candidate(cargo_id="B"), 300.0, ["base"])
        first = ScoredCandidate(_candidate(cargo_id="A"), 300.0, ["base"])

        reranked = rerank_scored_candidates([second, first], [], weights=LearningToRankWeights())

        self.assertEqual([item.candidate.cargo_id for item in reranked], ["A", "B"])

    def test_hard_no_drive_window_feature_penalizes_crossing_candidate(self):
        crossing = ScoredCandidate(
            _candidate(
                cargo_id="CROSS",
                rough_net_value=330.0,
                pickup_minutes=20,
                cost_time_minutes=70,
                estimated_finish_minute=24 * 60 + 30,
            ),
            330.0,
            ["base"],
        )
        safe = ScoredCandidate(
            _candidate(
                cargo_id="SAFE",
                rough_net_value=300.0,
                pickup_minutes=15,
                cost_time_minutes=45,
                estimated_finish_minute=22 * 60 + 30,
            ),
            300.0,
            ["base"],
        )
        rules = [
            PreferenceRule(
                RuleType.NO_DRIVE_WINDOW,
                RuleStrength.HARD,
                {"start_minute": 23 * 60, "end_minute": 6 * 60, "cross_day": True},
                "night window",
            )
        ]
        weights = LearningToRankWeights(no_drive_window_risk=-80.0)

        reranked = rerank_scored_candidates([crossing, safe], rules, weights=weights)

        self.assertEqual([item.candidate.cargo_id for item in reranked], ["SAFE", "CROSS"])

    def test_zero_future_market_weight_does_not_call_heatmap(self):
        class RaisingHeatmap:
            def future_value(self, *args, **kwargs):
                raise AssertionError("future market should not be called when its weight is zero")

        candidate = ScoredCandidate(_candidate(cargo_id="A"), 300.0, ["base"])

        reranked = rerank_scored_candidates(
            [candidate],
            [],
            market_heatmap=RaisingHeatmap(),
            weights=LearningToRankWeights(value_per_minute=1.0, future_market_value=0.0),
        )

        self.assertEqual(reranked[0].candidate.cargo_id, "A")


if __name__ == "__main__":
    unittest.main()
