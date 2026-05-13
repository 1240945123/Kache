from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Callable, Iterable

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
    "须",
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
        _parse_monthly_off_days,
        _parse_forbidden_zone,
        _parse_home_deadline,
        _parse_sequence_task,
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


def parse_preferences_with_fallback(
    preferences: Iterable[Any],
    model_parse_fn: Callable[[str], Any] | None = None,
    max_model_calls: int = 2,
) -> list[PreferenceRule]:
    rules = parse_preferences(preferences)
    if model_parse_fn is None or max_model_calls <= 0:
        return rules

    fallback_rules: list[PreferenceRule] = []
    calls = 0
    for rule in rules:
        if rule.rule_type != RuleType.UNKNOWN or rule.strength != RuleStrength.UNKNOWN_STRONG or calls >= max_model_calls:
            fallback_rules.append(rule)
            continue

        calls += 1
        parsed_rule = _model_payload_to_rule(model_parse_fn, rule)
        fallback_rules.append(parsed_rule or rule)
    return fallback_rules


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


def _model_payload_to_rule(model_parse_fn: Callable[[str], Any], original_rule: PreferenceRule) -> PreferenceRule | None:
    try:
        payload = model_parse_fn(original_rule.source_text)
    except Exception:
        return None

    if isinstance(payload, PreferenceRule):
        return payload
    if not isinstance(payload, dict):
        return None

    try:
        rule_type = _coerce_rule_type(payload.get("rule_type") or payload.get("type"))
        strength = _coerce_rule_strength(payload.get("strength"), original_rule.strength)
        value = payload.get("value", {})
        source_text = payload.get("source_text") or original_rule.source_text
    except (TypeError, ValueError):
        return None

    if rule_type is None or not isinstance(value, dict):
        return None
    return PreferenceRule(rule_type, strength, value, source_text)


def _coerce_rule_type(value: Any) -> RuleType | None:
    if isinstance(value, RuleType):
        return value
    if isinstance(value, str):
        return RuleType(value)
    return None


def _coerce_rule_strength(value: Any, default: RuleStrength) -> RuleStrength:
    if isinstance(value, RuleStrength):
        return value
    if isinstance(value, str):
        return RuleStrength(value)
    return default


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


def _parse_monthly_off_days(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(
        r"(?:每月|自然月内).*?至少(?:要有)?\s*(\d+)\s*个?整天.*?(?:不接单).*?(?:不空车|空车乱跑)",
        text,
    )
    if not match:
        return None
    return (
        match.start(),
        PreferenceRule(
            RuleType.MONTHLY_OFF_DAYS,
            strength,
            {"required_days": int(match.group(1))},
            text,
        ),
    )


def _parse_forbidden_zone(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(
        r"(?:不得|不能|禁止).*?进入.*?[（(]\s*(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)\s*[）)].*?半径\s*(\d+(?:\.\d+)?)\s*公里",
        text,
    )
    if not match:
        return None
    return (
        match.start(),
        PreferenceRule(
            RuleType.FORBIDDEN_ZONE,
            strength,
            {
                "lat": float(match.group(1)),
                "lng": float(match.group(2)),
                "radius_km": float(match.group(3)),
            },
            text,
        ),
    )


def _parse_home_deadline(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(
        r"每天\s*(\d{1,2})\s*点前.*?(?:须|必须|务必).*?(?:自家位置|家|老家).*?[（(]\s*(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)\s*[）)].*?([一二三四五六七八九十\d.]+)\s*公里内",
        text,
    )
    if not match:
        return None
    return (
        match.start(),
        PreferenceRule(
            RuleType.HOME_DEADLINE,
            strength,
            {
                "deadline_minute": int(match.group(1)) * 60,
                "lat": float(match.group(2)),
                "lng": float(match.group(3)),
                "radius_km": _distance_number(match.group(4)),
            },
            text,
        ),
    )


def _parse_sequence_task(text: str, strength: RuleStrength) -> tuple[int, PreferenceRule] | None:
    match = re.search(
        r"(?:须|必须).*?先到[（(]\s*(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)\s*[）)].*?配偶.*?不少于\s*(\d+)\s*分钟.*?再返回老家[（(]\s*(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)\s*[）)].*?须在\s*(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日\s*(\d{1,2}):(\d{2})\s*前进家门.*?至少待到\s*(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日\s*(\d{1,2}):(\d{2})",
        text,
    )
    if not match:
        return None

    deadline = _format_datetime(match.group(6), match.group(7), match.group(8), match.group(9), match.group(10))
    stay_until = _format_datetime(match.group(11), match.group(12), match.group(13), match.group(14), match.group(15))
    return (
        match.start(),
        PreferenceRule(
            RuleType.SEQUENCE_TASK,
            strength,
            {
                "steps": [
                    {
                        "action": "pickup",
                        "lat": float(match.group(1)),
                        "lng": float(match.group(2)),
                        "target": "spouse",
                        "wait_minutes": int(match.group(3)),
                    },
                    {
                        "action": "return_home",
                        "lat": float(match.group(4)),
                        "lng": float(match.group(5)),
                        "target": "hometown",
                    },
                ],
                "deadline": deadline,
                "stay_until": stay_until,
            },
            text,
        ),
    )


def _format_datetime(year: str, month: str, day: str, hour: str, minute: str) -> str:
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d} {int(hour):02d}:{int(minute):02d}:00"


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
