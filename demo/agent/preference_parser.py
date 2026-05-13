from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Iterable

from preference_rules import PreferenceRule, RuleStrength, RuleType


_HARD_WORDS = (
    "必须",
    "务必",
    "不得",
    "不能",
    "禁止",
    "不接",
    "罚",
    "违约",
    "指定",
    "至少",
)
_SOFT_WORDS = (
    "尽量",
    "尽可能",
    "最好",
    "优先",
    "希望",
    "可以的话",
    "best-effort",
    "try",
)


def classify_strength(text: str) -> RuleStrength:
    normalized = str(text or "").strip().lower()
    if any(word in normalized for word in _HARD_WORDS):
        return RuleStrength.HARD
    if any(word in normalized for word in _SOFT_WORDS):
        return RuleStrength.SOFT
    return RuleStrength.UNKNOWN


@lru_cache(maxsize=512)
def parse_preference_text(text: str) -> list[PreferenceRule]:
    normalized = str(text or "").strip()
    if not normalized:
        return []

    strength = classify_strength(normalized)
    matches: list[tuple[int, PreferenceRule]] = []

    category_rule = _parse_forbidden_categories(normalized, strength)
    if category_rule is not None:
        matches.append((0, category_rule))

    for parser in (
        _parse_no_drive_window,
        _parse_daily_rest,
        _parse_required_cargo,
        _parse_monthly_visit_days,
    ):
        parsed = parser(normalized, strength)
        if parsed is not None:
            position, rule = parsed
            matches.append((position, rule))

    matches.extend(_parse_distance_limits(normalized, strength))

    if not matches:
        return [PreferenceRule(RuleType.UNKNOWN, strength, normalized, {})]

    matches.sort(key=lambda item: item[0])
    return [rule for _, rule in matches]


def parse_preferences(preferences: Iterable[Any]) -> list[PreferenceRule]:
    seen: set[str] = set()
    rules: list[PreferenceRule] = []
    for preference in preferences:
        text = _preference_text(preference)
        if not text or text in seen:
            continue
        seen.add(text)
        rules.extend(parse_preference_text(text))
    return rules


def _preference_text(preference: Any) -> str:
    if isinstance(preference, str):
        return preference.strip()
    if isinstance(preference, dict):
        for key in ("text", "preference", "preference_text", "content"):
            value = preference.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""
    for attr in ("text", "preference", "preference_text", "content"):
        value = getattr(preference, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _parse_forbidden_categories(text: str, strength: RuleStrength) -> PreferenceRule | None:
    if not any(word in text for word in ("不接", "禁止", "不要", "不拉")):
        return None
    categories = re.findall(r"[“\"']([^”\"']+)[”\"']", text)
    if not categories:
        return None
    return PreferenceRule(
        RuleType.CARGO_CATEGORY,
        strength,
        text,
        {"forbidden_categories": categories},
    )


def _parse_no_drive_window(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(r"每天\s*(\d{1,2})\s*点\s*(?:至|到|-)\s*(次日)?\s*(\d{1,2})\s*点", text)
    if not match:
        return None
    start_hour = int(match.group(1))
    end_hour = int(match.group(3))
    restrictions: list[str] = []
    if "不接单" in text:
        restrictions.append("no_order")
    if "不空车赶路" in text or "不空驶" in text or "不空车" in text:
        restrictions.append("no_deadhead")
    return (
        match.start(),
        PreferenceRule(
            RuleType.NO_DRIVE_WINDOW,
            strength,
            text,
            {
                "start_hour": start_hour,
                "end_hour": end_hour,
                "crosses_day": bool(match.group(2)) or end_hour <= start_hour,
                "restrictions": restrictions,
            },
        ),
    )


def _parse_daily_rest(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(r"每天.*?(至少)?.*?(连着|连续)?.*?停车休息.*?满?\s*(\d+(?:\.\d+)?)\s*小时", text)
    if not match:
        return None
    return (
        match.start(),
        PreferenceRule(
            RuleType.DAILY_REST,
            strength,
            text,
            {
                "min_hours": _number(match.group(3)),
                "continuous": "连着" in text or "连续" in text,
            },
        ),
    )


def _parse_distance_limits(text: str, strength: RuleStrength) -> list[tuple[int, PreferenceRule]]:
    rules: list[tuple[int, PreferenceRule]] = []
    patterns = (
        (RuleType.PICKUP_DISTANCE_LIMIT, r"(?:接货|提货|取货|装货)距离[^，。；;]*?(?:不超过|不超|最多|以内|不大于)\s*(\d+(?:\.\d+)?)\s*公里"),
        (RuleType.HAUL_DISTANCE_LIMIT, r"(?:运输|运距|拉货|货运)距离[^，。；;]*?(?:不超过|不超|最多|以内|不大于)\s*(\d+(?:\.\d+)?)\s*公里"),
    )
    for rule_type, pattern in patterns:
        for match in re.finditer(pattern, text):
            rules.append(
                (
                    match.start(),
                    PreferenceRule(rule_type, strength, text, {"max_km": _number(match.group(1))}),
                )
            )
    return rules


def _parse_monthly_visit_days(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(
        r"每月.*?(?:至少)?\s*(\d+)\s*天.*?坐标\s*[（(]\s*(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)\s*[）)].*?半径\s*(\d+(?:\.\d+)?)\s*公里",
        text,
    )
    if not match:
        return None
    return (
        match.start(),
        PreferenceRule(
            RuleType.MONTHLY_VISIT_DAYS,
            strength,
            text,
            {
                "min_days": int(match.group(1)),
                "lat": float(match.group(2)),
                "lng": float(match.group(3)),
                "radius_km": _number(match.group(4)),
            },
        ),
    )


def _parse_required_cargo(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(r"指定熟货源编号\s*([A-Za-z0-9_-]+)", text)
    if not match:
        return None
    return (
        match.start(),
        PreferenceRule(
            RuleType.REQUIRED_CARGO,
            strength,
            text,
            {"cargo_id": match.group(1)},
        ),
    )


def _number(value: str) -> int | float:
    parsed = float(value)
    if parsed.is_integer():
        return int(parsed)
    return parsed
