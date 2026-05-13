from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_decision_service import ModelDecisionService


class FakeApi:
    def __init__(self, *, status, cargo_items=None, history=None):
        self.status = status
        self.cargo_items = cargo_items or []
        self.history = history or {"records": []}
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


def _cargo(cargo_id="C1", category="普通货物", cargo_name=None):
    cargo = {
        "cargo_id": cargo_id,
        "category": category,
        "remove_time": "2026-03-01 23:59:59",
        "price": 500.0,
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


if __name__ == "__main__":
    unittest.main()
