from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

SIMULATION_EPOCH = datetime(2026, 3, 1, 0, 0, 0)
DEFAULT_SPEED_KM_PER_HOUR = 60.0
DEFAULT_COST_PER_KM = 1.5
DEFAULT_TOP_CANDIDATE_LIMIT = 10
DEFAULT_FALLBACK_WAIT_MINUTES = 30
MAX_TOTAL_ORDER_MINUTES = 12 * 60


@dataclass(frozen=True)
class Candidate:
    cargo_id: str
    price: float
    pickup_distance_km: float
    pickup_minutes: int
    wait_minutes: int
    cost_time_minutes: int
    estimated_finish_minute: int
    haul_distance_km: float
    rough_net_value: float
    value_per_minute: float
    start: dict[str, Any]
    end: dict[str, Any]
    load_time: Any

    def to_prompt_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["price"] = round(self.price, 2)
        data["pickup_distance_km"] = round(self.pickup_distance_km, 2)
        data["haul_distance_km"] = round(self.haul_distance_km, 2)
        data["rough_net_value"] = round(self.rough_net_value, 2)
        data["value_per_minute"] = round(self.value_per_minute, 4)
        return data


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    p1 = math.radians(lat1)
    l1 = math.radians(lng1)
    p2 = math.radians(lat2)
    l2 = math.radians(lng2)
    dp = p2 - p1
    dl = l2 - l1
    h = math.sin(dp * 0.5) ** 2 + math.cos(p1) * math.cos(p2) * (math.sin(dl * 0.5) ** 2)
    h = min(1.0, max(0.0, h))
    return 2.0 * radius_km * math.asin(math.sqrt(h))


def movement_minutes(distance_km: float, speed_km_per_hour: float = DEFAULT_SPEED_KM_PER_HOUR) -> int:
    if distance_km <= 1e-6:
        return 0
    return max(1, math.ceil((distance_km / speed_km_per_hour) * 60))


def wall_time_to_minutes(text: str) -> int:
    dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M:%S")
    return int((dt - SIMULATION_EPOCH).total_seconds() // 60)


@lru_cache(maxsize=1)
def resolve_simulation_horizon_minutes() -> int | None:
    for path in (Path("config/config.json"), Path("server/config/config.json")):
        if not path.is_file():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            days = int(raw.get("simulation_duration_days", 0))
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            continue
        if days > 0:
            return days * 24 * 60
    return None


def _load_window_minutes(load_time: Any) -> tuple[int, int] | None:
    if load_time is None:
        return None
    if not isinstance(load_time, list) or len(load_time) != 2:
        return None
    left = str(load_time[0]).strip()
    right = str(load_time[1]).strip()
    if not left or not right:
        return None
    start = wall_time_to_minutes(left)
    end = wall_time_to_minutes(right)
    if end < start:
        return None
    return start, end


def _truck_length_allowed(cargo: dict[str, Any], driver_truck_length: str) -> bool:
    allowed = cargo.get("truck_length")
    if not allowed or not driver_truck_length:
        return True
    if isinstance(allowed, list):
        return str(driver_truck_length) in {str(item) for item in allowed}
    return str(allowed) == str(driver_truck_length)


def build_candidate(
    item: dict[str, Any],
    status: dict[str, Any],
    *,
    speed_km_per_hour: float = DEFAULT_SPEED_KM_PER_HOUR,
    cost_per_km: float = DEFAULT_COST_PER_KM,
    horizon_minutes: int | None = None,
) -> Candidate | None:
    try:
        cargo = item.get("cargo")
        if not isinstance(cargo, dict):
            return None
        cargo_id = str(cargo.get("cargo_id", "")).strip()
        if not cargo_id:
            return None
        price = float(cargo.get("price", 0.0))
        if price <= 0:
            return None
        cost_time_minutes = int(cargo.get("cost_time_minutes"))
        if cost_time_minutes < 0:
            return None
        driver_truck_length = str(status.get("truck_length", "")).strip()
        if not _truck_length_allowed(cargo, driver_truck_length):
            return None
        current_lat = float(status["current_lat"])
        current_lng = float(status["current_lng"])
        current_minute = int(status.get("simulation_progress_minutes", 0))
        start = cargo.get("start")
        end = cargo.get("end")
        if not isinstance(start, dict) or not isinstance(end, dict):
            return None
        start_lat = float(start["lat"])
        start_lng = float(start["lng"])
        end_lat = float(end["lat"])
        end_lng = float(end["lng"])
    except (KeyError, TypeError, ValueError):
        return None

    pickup_distance_km = haversine_km(current_lat, current_lng, start_lat, start_lng)
    pickup_minutes = movement_minutes(pickup_distance_km, speed_km_per_hour=speed_km_per_hour)
    arrival_minute = current_minute + pickup_minutes
    remove_time = str(cargo.get("remove_time", "")).strip()
    if remove_time and arrival_minute > wall_time_to_minutes(remove_time):
        return None
    window = _load_window_minutes(cargo.get("load_time"))
    wait_minutes = 0
    if window is not None:
        load_start, load_end = window
        if arrival_minute > load_end:
            return None
        wait_minutes = max(0, load_start - arrival_minute)
    estimated_finish_minute = arrival_minute + wait_minutes + cost_time_minutes
    effective_horizon = horizon_minutes if horizon_minutes is not None else resolve_simulation_horizon_minutes()
    if effective_horizon is not None and estimated_finish_minute > effective_horizon:
        return None
    total_order_minutes = estimated_finish_minute - current_minute
    if total_order_minutes > MAX_TOTAL_ORDER_MINUTES:
        return None
    haul_distance_km = haversine_km(start_lat, start_lng, end_lat, end_lng)
    rough_cost = (pickup_distance_km + haul_distance_km) * cost_per_km
    rough_net_value = price - rough_cost
    if rough_net_value <= 0:
        return None
    value_per_minute = rough_net_value / max(1, total_order_minutes)
    return Candidate(
        cargo_id=cargo_id,
        price=price,
        pickup_distance_km=pickup_distance_km,
        pickup_minutes=pickup_minutes,
        wait_minutes=wait_minutes,
        cost_time_minutes=cost_time_minutes,
        estimated_finish_minute=estimated_finish_minute,
        haul_distance_km=haul_distance_km,
        rough_net_value=rough_net_value,
        value_per_minute=value_per_minute,
        start=start,
        end=end,
        load_time=cargo.get("load_time"),
    )


def filter_and_rank_candidates(
    items: list[dict[str, Any]],
    status: dict[str, Any],
    *,
    limit: int = DEFAULT_TOP_CANDIDATE_LIMIT,
    horizon_minutes: int | None = None,
) -> list[Candidate]:
    candidates = [
        candidate
        for item in items
        if (candidate := build_candidate(item, status, horizon_minutes=horizon_minutes)) is not None
    ]
    candidates.sort(
        key=lambda c: (
            -c.rough_net_value,
            -c.value_per_minute,
            c.pickup_distance_km,
            c.estimated_finish_minute,
        )
    )
    return candidates[:limit]


def fallback_wait_action(duration_minutes: int = DEFAULT_FALLBACK_WAIT_MINUTES) -> dict[str, Any]:
    return {"action": "wait", "params": {"duration_minutes": int(duration_minutes)}}


def take_top_candidate_action(candidates: list[Candidate]) -> dict[str, Any]:
    if not candidates:
        return fallback_wait_action()
    return {"action": "take_order", "params": {"cargo_id": candidates[0].cargo_id}}


def parse_model_action(model_resp: dict[str, Any], *, allowed_cargo_ids: set[str]) -> dict[str, Any]:
    try:
        choices = model_resp.get("choices")
        if not isinstance(choices, list) or not choices:
            return fallback_wait_action()
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            return fallback_wait_action()
        action = json.loads(content)
        if not isinstance(action, dict):
            return fallback_wait_action()
        action_name = str(action.get("action", "")).strip().lower()
        params = action.get("params")
        if not isinstance(params, dict):
            return fallback_wait_action()
        if action_name == "take_order":
            cargo_id = str(params.get("cargo_id", "")).strip()
            if cargo_id not in allowed_cargo_ids:
                return fallback_wait_action()
            return {"action": "take_order", "params": {"cargo_id": cargo_id}}
        if action_name == "reposition":
            latitude = float(params["latitude"])
            longitude = float(params["longitude"])
            return {"action": "reposition", "params": {"latitude": latitude, "longitude": longitude}}
        if action_name == "wait":
            duration_minutes = int(params["duration_minutes"])
            if duration_minutes <= 0:
                return fallback_wait_action()
            return {"action": "wait", "params": {"duration_minutes": duration_minutes}}
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return fallback_wait_action()
    return fallback_wait_action()
