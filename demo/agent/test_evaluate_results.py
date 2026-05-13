from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evaluate_results import build_report


class EvaluateResultsTest(unittest.TestCase):
    def test_build_report_includes_summary_drivers_and_action_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp)
            (results_dir / "monthly_income_202603.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "total_net_income_all_drivers": 100.0,
                            "total_preference_penalty": 20.0,
                            "failed_driver_count": 0,
                            "total_token_usage": {"total_tokens": 5},
                        },
                        "drivers": [
                            {
                                "driver_id": "D001",
                                "income": {
                                    "gross_income": 200.0,
                                    "cost": 50.0,
                                    "preference_penalty": 20.0,
                                    "net_income": 130.0,
                                },
                                "calculation_aborted": False,
                                "preference_check": {"rules": [{"rule": "sample"}]},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (results_dir / "run_summary_202603.json").write_text(
                json.dumps(
                    {
                        "simulate_time_seconds": 3.5,
                        "simulation_duration_days": 30,
                        "simulation_max_steps": 20000,
                        "completed_steps": 42,
                    }
                ),
                encoding="utf-8",
            )
            (results_dir / "actions_202603_D001_sample.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"action": {"action": "take_order"}, "result": {"accepted": True}}),
                        json.dumps({"action": {"action": "wait"}, "result": {}}),
                    ]
                ),
                encoding="utf-8",
            )

            report = build_report(results_dir, experiment_id="unit-test")

        self.assertIn("# Experiment unit-test", report)
        self.assertIn("total_net_income_all_drivers", report)
        self.assertIn("completed_steps", report)
        self.assertIn("| D001 | 200.0 | 50.0 | 20.0 | 130.0 |", report)
        self.assertIn("take_order=1", report)


if __name__ == "__main__":
    unittest.main()
