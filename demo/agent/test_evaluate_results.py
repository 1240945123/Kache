from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
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
                "rules": 1,
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
                        "rules": 1,
                        "actions": {"take_order": 1, "wait": 1},
                    }
                ],
            }
        )

        self.assertIn("| D001 | 200.0 | 50.0 | 20.0 | 130.0 | False | 1 |", report)
        self.assertIn("- Generated at: 2026-05-14T12:34:56", report)

    def test_malformed_driver_rows_and_rules_do_not_crash_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp)
            (results_dir / "monthly_income_202603.json").write_text(
                json.dumps(
                    {
                        "summary": {},
                        "drivers": [
                            "not-a-driver-row",
                            {
                                "driver_id": "D001",
                                "income": {
                                    "gross_income": 200.0,
                                    "cost": 50.0,
                                    "preference_penalty": 20.0,
                                    "net_income": 130.0,
                                },
                                "calculation_aborted": False,
                                "preference_check": {"rules": {"malformed": "rules"}},
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = build_report(results_dir, experiment_id="unit-test")
            summary = build_experiment_summary(results_dir, experiment_id="unit-test")

        self.assertEqual(summary["drivers"][0]["rules"], 0)
        self.assertIn("| D001 | 200.0 | 50.0 | 20.0 | 130.0 | False | 0 |", report)

        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp)
            (results_dir / "monthly_income_202603.json").write_text(
                json.dumps({"summary": {}, "drivers": {"unexpected": "shape"}}),
                encoding="utf-8",
            )

            report = build_report(results_dir, experiment_id="unit-test")
            summary = build_experiment_summary(results_dir, experiment_id="unit-test")

        self.assertEqual(summary["drivers"], [])
        self.assertIn("## Drivers", report)

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

    def test_compute_experiment_delta_includes_summary_run_and_driver_deltas_sorted_by_regression(self):
        current = {
            "summary": {
                "total_net_income_all_drivers": 150.0,
                "total_preference_penalty": 35.0,
                "failed_driver_count": 2,
                "total_token_usage": {"total_tokens": 120},
            },
            "run_summary": {
                "completed_steps": 42,
                "simulate_time_seconds": 12.5,
                "simulation_duration_days": 30,
            },
            "drivers": [
                {
                    "driver_id": "D002",
                    "gross": 90.0,
                    "cost": 10.0,
                    "penalty": 10.0,
                    "net": 70.0,
                    "actions": {"take_order": 2, "wait": 1},
                },
                {
                    "driver_id": "D001",
                    "gross": 120.0,
                    "cost": 20.0,
                    "penalty": 25.0,
                    "net": 75.0,
                    "actions": {"take_order": 3, "accepted_false": 1},
                },
                {
                    "driver_id": "D003",
                    "gross": 70.0,
                    "cost": 10.0,
                    "penalty": 5.0,
                    "net": 55.0,
                    "actions": {"wait": 2},
                },
            ],
        }
        baseline = {
            "summary": {
                "total_net_income_all_drivers": 140.0,
                "total_preference_penalty": 20.0,
                "failed_driver_count": 1,
                "total_token_usage": {"total_tokens": 100},
            },
            "run_summary": {
                "completed_steps": 40,
                "simulate_time_seconds": 10.0,
                "simulation_duration_days": 30,
            },
            "drivers": [
                {
                    "driver_id": "D001",
                    "gross": 100.0,
                    "cost": 20.0,
                    "penalty": 5.0,
                    "net": 75.0,
                    "actions": {"take_order": 5, "accepted_false": 1},
                },
                {
                    "driver_id": "D002",
                    "gross": 90.0,
                    "cost": 10.0,
                    "penalty": 0.0,
                    "net": 80.0,
                    "actions": {"take_order": 1, "wait": 1},
                },
                {
                    "driver_id": "D003",
                    "gross": 65.0,
                    "cost": 10.0,
                    "penalty": 0.0,
                    "net": 55.0,
                    "actions": {"wait": 1},
                },
            ],
        }

        delta = evaluate_results.compute_experiment_delta(current, baseline)

        self.assertEqual(
            delta["summary"],
            {
                "total_net_income_all_drivers": 10.0,
                "total_preference_penalty": 15.0,
                "failed_driver_count": 1.0,
                "total_token_usage.total_tokens": 20.0,
            },
        )
        self.assertEqual(
            delta["run_summary"],
            {
                "completed_steps": 2.0,
                "simulate_time_seconds": 2.5,
            },
        )
        self.assertEqual([row["driver_id"] for row in delta["drivers"]], ["D001", "D002", "D003"])
        self.assertEqual(
            delta["drivers"][0],
            {
                "driver_id": "D001",
                "gross": 20.0,
                "cost": 0.0,
                "penalty": 20.0,
                "net": 0.0,
                "actions": {"accepted_false": 0.0, "take_order": -2.0},
            },
        )
        self.assertEqual(delta["drivers"][1]["penalty"], 10.0)
        self.assertEqual(delta["drivers"][1]["net"], -10.0)
        self.assertEqual(delta["drivers"][2]["penalty"], 5.0)
        self.assertEqual(delta["drivers"][2]["net"], 0.0)

    def test_format_delta_section_reads_json_baseline_and_formats_signed_values(self):
        experiment = {
            "summary": {
                "total_net_income_all_drivers": 150.0,
                "total_preference_penalty": 25.0,
                "failed_driver_count": 0,
                "total_token_usage": {"total_tokens": 110},
            },
            "run_summary": {"completed_steps": 42, "simulate_time_seconds": 12.0},
            "drivers": [
                {
                    "driver_id": "D001",
                    "gross": 120.0,
                    "cost": 20.0,
                    "penalty": 3.0,
                    "net": 97.0,
                    "actions": {"take_order": 4},
                }
            ],
        }
        baseline = {
            "summary": {
                "total_net_income_all_drivers": 140.0,
                "total_preference_penalty": 27.0,
                "failed_driver_count": 0,
                "total_token_usage": {"total_tokens": 100},
            },
            "run_summary": {"completed_steps": 40, "simulate_time_seconds": 10.0},
            "drivers": [
                {
                    "driver_id": "D001",
                    "gross": 100.0,
                    "cost": 20.0,
                    "penalty": 5.0,
                    "net": 75.0,
                    "actions": {"take_order": 4},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            baseline_path = Path(tmp) / "baseline.json"
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

            lines = evaluate_results.format_delta_section(experiment, baseline_path)

        section = "\n".join(lines)
        self.assertIn("## Delta", section)
        self.assertIn("- total_net_income_all_drivers: +10.0", section)
        self.assertIn("- total_preference_penalty: -2.0", section)
        self.assertIn("- total_token_usage.total_tokens: +10.0", section)
        self.assertIn("| D001 | +20.0 | +0.0 | -2.0 | +22.0 |", section)

    def test_main_writes_markdown_and_json_sidecar_and_passes_optional_args(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            out_dir = root / "reports"
            results_dir.mkdir()
            (results_dir / "monthly_income_202603.json").write_text(
                json.dumps({"summary": {}, "drivers": []}),
                encoding="utf-8",
            )
            baseline_path = root / "baseline.json"
            baseline_path.write_text(json.dumps({"summary": {}, "drivers": []}), encoding="utf-8")
            captured = {}
            original_format_report = evaluate_results.format_report
            original_argv = sys.argv

            def capture_format_report(experiment, *, baseline_path=None, timeline_driver_ids=None):
                captured["experiment"] = experiment
                captured["baseline_path"] = baseline_path
                captured["timeline_driver_ids"] = timeline_driver_ids
                return "report\n"

            sys.argv = [
                "evaluate_results.py",
                "--results-dir",
                str(results_dir),
                "--out-dir",
                str(out_dir),
                "--experiment-id",
                "unit-test",
                "--baseline",
                str(baseline_path),
                "--timeline-driver",
                "D001",
                "--timeline-driver",
                "D002",
            ]
            output = StringIO()
            try:
                evaluate_results.format_report = capture_format_report
                with redirect_stdout(output):
                    evaluate_results.main()
            finally:
                evaluate_results.format_report = original_format_report
                sys.argv = original_argv

            self.assertEqual(captured["baseline_path"], baseline_path)
            self.assertEqual(captured["timeline_driver_ids"], ["D001", "D002"])
            self.assertEqual(captured["experiment"]["experiment_id"], "unit-test")
            self.assertTrue((out_dir / "unit-test.md").exists())
            self.assertTrue((out_dir / "unit-test.json").exists())
            self.assertEqual(
                json.loads((out_dir / "unit-test.json").read_text(encoding="utf-8"))["experiment_id"],
                "unit-test",
            )
            self.assertIn(str(out_dir / "unit-test.md"), output.getvalue())
            self.assertIn(str(out_dir / "unit-test.json"), output.getvalue())


if __name__ == "__main__":
    unittest.main()
