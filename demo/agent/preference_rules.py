from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RuleStrength(str, Enum):
    HARD = "hard"
    SOFT = "soft"
    UNKNOWN = "unknown"


class RuleType(str, Enum):
    CARGO_CATEGORY = "cargo_category"
    NO_DRIVE_WINDOW = "no_drive_window"
    DAILY_REST = "daily_rest"
    MONTHLY_NO_ORDER_DAYS = "monthly_no_order_days"
    MONTHLY_OFF_DAYS = "monthly_off_days"
    MONTHLY_VISIT_DAYS = "monthly_visit_days"
    PICKUP_DISTANCE_LIMIT = "pickup_distance_limit"
    HAUL_DISTANCE_LIMIT = "haul_distance_limit"
    MONTHLY_DEADHEAD_LIMIT = "monthly_deadhead_limit"
    FORBIDDEN_ZONE = "forbidden_zone"
    BOUNDING_BOX = "bounding_box"
    REQUIRED_CARGO = "required_cargo"
    HOME_DEADLINE = "home_deadline"
    STAY_WINDOW = "stay_window"
    SEQUENCE_TASK = "sequence_task"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PreferenceRule:
    rule_type: RuleType
    strength: RuleStrength
    text: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlannedIntent:
    rules: list[PreferenceRule] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
