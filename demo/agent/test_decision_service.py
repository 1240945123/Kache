from __future__ import annotations

import sys
import subprocess
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_decision_service import ModelDecisionService


class FakeApi:
    def __init__(self, *, status, cargo_items=None, history=None, model_response=None):
        self.status = status
        self.cargo_items = cargo_items or []
        self.history = history or {"records": []}
        self.model_response = model_response
        self.query_count = 0
        self.model_count = 0

    def get_driver_status(self, driver_id):
        return dict(self.status, driver_id=driver_id)

    def query_cargo(self, driver_id, latitude, longitude):
        self.query_count += 1
        return {"driver_id": driver_id, "items": self.cargo_items}

    def query_decision_history(self, driver_id, step):
        return self.history

    def model_chat_completion(self, payload):
        self.model_count += 1
        if self.model_response is not None:
            return self.model_response
        raise AssertionError("model should not drive normal decisions")


def _status(**overrides):
    base = {
        "current_lat": 22.54,
        "current_lng": 114.06,
        "truck_length": "4.2米",
        "completed_order_count": 0,
        "simulation_progress_minutes": 23 * 60 + 10,
        "preferences": ["每天23点至次日6点不接单、不空车赶路。"],
    }
    base.update(overrides)
    return base


def _cargo(cargo_id="C1", category="普通货物", cargo_name=None, price=500.0):
    cargo = {
        "cargo_id": cargo_id,
        "category": category,
        "remove_time": "2026-03-01 23:59:59",
        "price": price,
        "cost_time_minutes": 100,
        "load_time": None,
        "truck_length": ["4.2米"],
        "start": {"lat": 22.55, "lng": 114.07},
        "end": {"lat": 22.6, "lng": 114.08},
    }
    if cargo_name is not None:
        cargo["cargo_name"] = cargo_name
    return {"distance_km": 1.0, "cargo": cargo}


class DecisionServiceTest(unittest.TestCase):
    def test_decision_service_imports_from_demo_package_context(self):
        demo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-c", "from agent.model_decision_service import ModelDecisionService"],
            cwd=demo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_waits_without_querying_cargo_during_no_drive_window(self):
        api = FakeApi(status=_status())

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action["action"], "wait")
        self.assertEqual(api.query_count, 0)

    def test_takes_safe_candidate_outside_window_without_model(self):
        api = FakeApi(status=_status(simulation_progress_minutes=8 * 60, preferences=[]), cargo_items=[_cargo()])

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action, {"action": "take_order", "params": {"cargo_id": "C1"}})
        self.assertEqual(api.model_count, 0)

    def test_forbidden_category_candidate_falls_back_to_wait(self):
        api = FakeApi(
            status=_status(
                simulation_progress_minutes=8 * 60,
                preferences=["不接货源品类为「煤炭矿产」的订单。"],
            ),
            cargo_items=[_cargo(category="煤炭矿产", cargo_name="煤炭矿产")],
        )

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action["action"], "wait")

    def test_required_cargo_restricts_candidates_before_scoring(self):
        api = FakeApi(
            status=_status(
                simulation_progress_minutes=8 * 60,
                preferences=["指定熟货源编号240646"],
            ),
            cargo_items=[
                _cargo(cargo_id="OTHER", price=900.0),
                _cargo(cargo_id="240646", price=300.0),
            ],
        )

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action, {"action": "take_order", "params": {"cargo_id": "240646"}})

    def test_required_cargo_not_visible_waits(self):
        api = FakeApi(
            status=_status(
                simulation_progress_minutes=8 * 60,
                preferences=["指定熟货源编号240646"],
            ),
            cargo_items=[_cargo(cargo_id="OTHER", price=900.0)],
        )

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action["action"], "wait")

    def test_known_monthly_off_rule_does_not_block_safe_candidate(self):
        monthly_off = (
            "\u81ea\u7136\u6708\u5185\u81f3\u5c11\u8981\u67092\u4e2a"
            "\u6574\u5929\u65e2\u4e0d\u63a5\u5355\u4e5f\u4e0d"
            "\u7a7a\u8f66\u4e71\u8dd1\u3002"
        )
        api = FakeApi(
            status=_status(simulation_progress_minutes=8 * 60, preferences=[monthly_off]),
            cargo_items=[_cargo()],
        )

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action, {"action": "take_order", "params": {"cargo_id": "C1"}})
        self.assertEqual(api.model_count, 0)

    def test_unenforced_hard_rule_from_model_fallback_waits(self):
        api = FakeApi(
            status=_status(
                simulation_progress_minutes=8 * 60,
                preferences=["必须按短信通知留在家中。"],
            ),
            cargo_items=[_cargo()],
            model_response={
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"rules":[{"rule_type":"stay_window","strength":"hard",'
                                '"value":{"location":"home"},"source_text":"必须按短信通知留在家中。"}]}'
                            )
                        }
                    }
                ]
            },
        )

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action["action"], "wait")
        self.assertEqual(api.model_count, 1)

    def test_no_drive_window_with_unknown_strong_does_not_call_model_or_query_cargo(self):
        api = FakeApi(
            status=_status(
                preferences=[
                    "每天23点至次日6点不接单、不空车赶路。",
                    "必须按短信通知留在家中。",
                ],
            ),
            cargo_items=[_cargo()],
        )

        action = ModelDecisionService(api).decide("DXXX")

        self.assertEqual(action["action"], "wait")
        self.assertEqual(api.model_count, 0)
        self.assertEqual(api.query_count, 0)


if __name__ == "__main__":
    unittest.main()
