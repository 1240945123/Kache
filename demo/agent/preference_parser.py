from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Iterable

from preference_rules import PreferenceRule, RuleStrength, RuleType


_STRONG_UNKNOWN_MARKERS = (
    "必须",
    "不得",
    "禁止",
    "须",
    "罚",
    "上不封顶",
    "临时约定",
    "不接",
    "不要",
)
_HARD_WORDS = (
    "必须",
    "务必",
    "不得",
    "不能",
    "禁止",
    "不接",
    "不要",
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
    if any(word in normalized for word in _SOFT_WORDS):
        return RuleStrength.SOFT
    if any(word in normalized for word in _HARD_WORDS):
        return RuleStrength.HARD
    return RuleStrength.UNKNOWN_SOFT


def parse_preference_text(text: str) -> list[PreferenceRule]:
    return list(_parse_preference_text_cached(str(text or "").strip()))


@lru_cache(maxsize=512)
def _parse_preference_text_cached(text: str) -> tuple[PreferenceRule, ...]:
    if not text:
        return ()

    strength = classify_strength(text)
    matches: list[tuple[int, PreferenceRule]] = []

    matches.extend(_parse_cargo_categories(text, strength))
    matches.extend(_parse_distance_limits(text, strength))

    for parser in (
        _parse_no_drive_window,
        _parse_daily_rest,
        _parse_required_cargo,
        _parse_monthly_visit_days,
    ):
        parsed = parser(text, strength)
        if parsed is not None:
            matches.append(parsed)

    if not matches:
        return (
            PreferenceRule(
                RuleType.UNKNOWN,
                _unknown_strength(text),
                {},
                text,
            ),
        )

    matches.sort(key=lambda item: item[0])
    return tuple(rule for _, rule in matches)


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


def _unknown_strength(text: str) -> RuleStrength:
    if any(marker in text for marker in _STRONG_UNKNOWN_MARKERS):
        return RuleStrength.UNKNOWN_STRONG
    return RuleStrength.UNKNOWN_SOFT


def _parse_cargo_categories(text: str, strength: RuleStrength) -> list[tuple[int, PreferenceRule]]:
    if not any(word in text for word in ("不接", "禁止", "不要", "不拉", "避免")):
        return []
    categories = [(match.start(), match.group(1).strip()) for match in re.finditer(r"[“\"'「]([^”\"'」]+)[”\"'」]", text)]
    if not categories:
        return []
    mode = "forbid" if strength == RuleStrength.HARD else "avoid"
    return [
        (
            position,
            PreferenceRule(
                RuleType.CARGO_CATEGORY,
                strength,
                {"category": category, "mode": mode},
                text,
            ),
        )
        for position, category in categories
    ]


def _parse_no_drive_window(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(r"每天\s*(\d{1,2})\s*点\s*(?:至|到|-)\s*(次日)?\s*(\d{1,2})\s*点", text)
    if not match:
        return None
    start_hour = int(match.group(1))
    end_hour = int(match.group(3))
    return (
        match.start(),
        PreferenceRule(
            RuleType.NO_DRIVE_WINDOW,
            strength,
            {
                "start_minute": start_hour * 60,
                "end_minute": end_hour * 60,
                "cross_day": bool(match.group(2)) or end_hour <= start_hour,
            },
            text,
        ),
    )


def _parse_daily_rest(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(r"每天.*?停车休息.*?满?\s*(\d+(?:\.\d+)?)\s*小时", text)
    if not match:
        return None
    return (
        match.start(),
        PreferenceRule(
            RuleType.DAILY_REST,
            strength,
            {"minutes": int(float(match.group(1)) * 60)},
            text,
        ),
    )


def _parse_distance_limits(text: str, strength: RuleStrength) -> list[tuple[int, PreferenceRule]]:
    rules: list[tuple[int, PreferenceRule]] = []
    patterns = (
        (
            RuleType.PICKUP_DISTANCE_LIMIT,
            r"(?:接货|提货|取货|装货|赴装货点空驶)距离[^，。；;]*?(?:不超过|不超|最多|以内|不大于|不得超过)\s*(\d+(?:\.\d+)?)\s*公里",
        ),
        (
            RuleType.HAUL_DISTANCE_LIMIT,
            r"(?:运输|运距|拉货|货运|单笔装卸)距离[^，。；;]*?(?:不超过|不超|最多|以内|不大于|不得超过)\s*(\d+(?:\.\d+)?)\s*公里",
        ),
    )
    for rule_type, pattern in patterns:
        for match in re.finditer(pattern, text):
            rules.append(
                (
                    match.start(),
                    PreferenceRule(rule_type, strength, {"km": float(match.group(1))}, text),
                )
            )
    return rules


def _parse_monthly_visit_days(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    parenthesized = re.search(
        r"(?:每月|自然月内).*?(?:至少)?\s*(\d+)\s*(?:个不同的自然日|天).*?[坐标到过]*[（(]\s*(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)\s*[）)].*?(?:半径\s*(\d+(?:\.\d+)?)|([一二三四五六七八九十]+))\s*公里?内?",
        text,
    )
    if parenthesized:
        radius_text = parenthesized.group(4) or parenthesized.group(5)
        return _monthly_visit_rule(parenthesized, strength, text, radius_text)

    with_coord_word = re.search(
        r"(?:每月|自然月内).*?(?:至少)?\s*(\d+)\s*(?:个不同的自然日|天).*?坐标\s*[（(]\s*(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)\s*[）)].*?半径\s*(\d+(?:\.\d+)?)\s*公里",
        text,
    )
    if with_coord_word:
        return _monthly_visit_rule(with_coord_word, strength, text, with_coord_word.group(4))
    return None


def _monthly_visit_rule(
    match: re.Match[str],
    strength: RuleStrength,
    text: str,
    radius_text: str | None,
) -> tuple[int, PreferenceRule]:
    return (
        match.start(),
        PreferenceRule(
            RuleType.MONTHLY_VISIT_DAYS,
            strength,
            {
                "required_days": int(match.group(1)),
                "lat": float(match.group(2)),
                "lng": float(match.group(3)),
                "radius_km": _distance_number(radius_text or "1"),
            },
            text,
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
            {"cargo_id": match.group(1)},
            text,
        ),
    )


def _distance_number(value: str) -> float:
    chinese_digits = {
        "一": 1.0,
        "二": 2.0,
        "三": 3.0,
        "四": 4.0,
        "五": 5.0,
        "六": 6.0,
        "七": 7.0,
        "八": 8.0,
        "九": 9.0,
        "十": 10.0,
    }
    if value in chinese_digits:
        return chinese_digits[value]
    return float(value)
