from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import demo.agent.evaluate_results as evaluate_results
from demo.agent.evaluate_results import build_experiment_summary, build_report, format_report


class EvaluateResultsTest(unittest.TestCase):
    def test_build_experiment_summary_extracts_structured_result_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp)
            (results_dir / "monthly_income_202603.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "total_net_income_all_drivers": 100.0,
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
                json.dumps({"completed_steps": 42}),
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

            summary = build_experiment_summary(results_dir, experiment_id="unit-test")

        self.assertEqual(summary["experiment_id"], "unit-test")
        self.assertIsInstance(summary["generated_at"], str)
        self.assertTrue(summary["generated_at"])
        self.assertEqual(summary["summary"]["total_net_income_all_drivers"], 100.0)
        self.assertEqual(summary["summary"]["total_token_usage"]["total_tokens"], 5)
        self.assertEqual(summary["run_summary"]["completed_steps"], 42)
        self.assertEqual(
            summary["drivers"][0],
            {
                "driver_id": "D001",
                "gross": 200.0,
                "cost": 50.0,
                "penalty": 20.0,
                "net": 130.0,
                "calculation_aborted": False,
                "rules": [{"rule": "sample"}],
                "actions": {"take_order": 1, "wait": 1},
            },
        )

    def test_format_report_uses_structured_driver_fields_and_generated_at(self):
        report = format_report(
            {
                "experiment_id": "unit-test",
                "generated_at": "2026-05-14T12:34:56",
                "results_dir": Path("results"),
                "summary": {},
                "run_summary": {},
                "drivers": [
                    {
                        "driver_id": "D001",
                        "gross": 200.0,
                        "cost": 50.0,
                        "penalty": 20.0,
                        "net": 130.0,
                        "calculation_aborted": False,
                        "rules": [{"rule": "sample"}],
                        "actions": {"take_order": 1, "wait": 1},
                    }
                ],
            }
        )

        self.assertIn("| D001 | 200.0 | 50.0 | 20.0 | 130.0 | False | 1 |", report)
        self.assertIn("- Generated at: 2026-05-14T12:34:56", report)

    def test_build_report_passes_optional_sections_to_formatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp)
            baseline_path = results_dir / "baseline.json"
            timeline_driver_ids = ["D001"]
            (results_dir / "monthly_income_202603.json").write_text(
                json.dumps({"summary": {}, "drivers": []}),
                encoding="utf-8",
            )
            captured = {}
            original_format_report = evaluate_results.format_report

            def capture_format_report(experiment, *, baseline_path=None, timeline_driver_ids=None):
                captured["baseline_path"] = baseline_path
                captured["timeline_driver_ids"] = timeline_driver_ids
                return "report\n"

            try:
                evaluate_results.format_report = capture_format_report
                report = evaluate_results.build_report(
                    results_dir,
                    experiment_id="unit-test",
                    baseline_path=baseline_path,
                    timeline_driver_ids=timeline_driver_ids,
                )
            finally:
                evaluate_results.format_report = original_format_report

        self.assertEqual(report, "report\n")
        self.assertEqual(captured["baseline_path"], baseline_path)
        self.assertEqual(captured["timeline_driver_ids"], timeline_driver_ids)

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
