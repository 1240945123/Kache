from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

SIMULATION_EPOCH = datetime(2026, 3, 1, 0, 0, 0)
DEFAULT_RADIUS_KM = 35.0
DEFAULT_HORIZON_MINUTES = 8 * 60
DEFAULT_MAX_BONUS = 500.0


@dataclass(frozen=True)
class MarketCargo:
    create_minute: int
    lat: float
    lng: float
    value: float


class MarketHeatmap:
    def __init__(self, records: list[MarketCargo]) -> None:
        self._records = tuple(sorted(records, key=lambda item: item.create_minute))

    @classmethod
    def from_cargo_records(cls, records: list[dict[str, Any]]) -> "MarketHeatmap":
        items: list[MarketCargo] = []
        for record in records:
            parsed = _parse_market_cargo(record)
            if parsed is not None:
                items.append(parsed)
        return cls(items)

    def future_value(
        self,
        latitude: float,
        longitude: float,
        *,
        current_minute: int,
        horizon_minutes: int = DEFAULT_HORIZON_MINUTES,
        radius_km: float = DEFAULT_RADIUS_KM,
        max_bonus: float = DEFAULT_MAX_BONUS,
    ) -> float:
        window_end = current_minute + max(0, int(horizon_minutes))
        total = 0.0
        for record in self._records:
            if record.create_minute <= current_minute:
                continue
            if record.create_minute > window_end:
                break
            distance_km = _haversine_km(latitude, longitude, record.lat, record.lng)
            if distance_km > radius_km:
                continue
            proximity = 1.0 - (distance_km / max(radius_km, 1e-6))
            total += 8.0 + (record.value * 0.015 * proximity)
        return min(float(max_bonus), round(total, 3))


@lru_cache(maxsize=1)
def load_default_market_heatmap() -> MarketHeatmap | None:
    for path in (
        Path("data/cargo_dataset.jsonl"),
        Path("server/data/cargo_dataset.jsonl"),
        Path("../server/data/cargo_dataset.jsonl"),
    ):
        if not path.is_file():
            continue
        records: list[dict[str, Any]] = []
        try:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except (OSError, json.JSONDecodeError):
            return None
        return MarketHeatmap.from_cargo_records(records)
    return None


def _parse_market_cargo(record: dict[str, Any]) -> MarketCargo | None:
    try:
        start = record["start"]
        return MarketCargo(
            create_minute=_create_minute(record),
            lat=float(start["lat"]),
            lng=float(start["lng"]),
            value=_price_value(record.get("price", 0.0)),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _create_minute(record: dict[str, Any]) -> int:
    if "create_minute" in record:
        return int(record["create_minute"])
    dt = datetime.strptime(str(record["create_time"]).strip(), "%Y-%m-%d %H:%M:%S")
    return int((dt - SIMULATION_EPOCH).total_seconds() // 60)


def _price_value(value: Any) -> float:
    price = float(value)
    return price / 100.0 if price > 10000.0 else price


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
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
