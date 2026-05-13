from __future__ import annotations

import unittest

from preference_parser import classify_strength, parse_preference_text, parse_preferences, parse_preferences_with_fallback
from preference_rules import PlannedIntent, PreferenceRule, RuleStrength, RuleType


def _only_rule(text: str):
    rules = parse_preference_text(text)
    assert len(rules) == 1
    return rules[0]


class PreferenceParserTest(unittest.TestCase):
    def test_rule_strength_has_expected_unknown_values(self):
        self.assertEqual(RuleStrength.UNKNOWN_STRONG.value, "unknown_strong")
        self.assertEqual(RuleStrength.UNKNOWN_SOFT.value, "unknown_soft")
        self.assertNotIn("UNKNOWN", RuleStrength.__members__)

    def test_planned_intent_fields(self):
        intent = PlannedIntent(
            intent_type="preference",
            action="avoid",
            params={"category": "test"},
            reason="user preference",
            priority=3,
        )

        self.assertEqual(intent.intent_type, "preference")
        self.assertEqual(intent.action, "avoid")
        self.assertEqual(intent.params, {"category": "test"})
        self.assertEqual(intent.reason, "user preference")
        self.assertEqual(intent.priority, 3)
        self.assertEqual(intent.metadata, {})

    def test_hard_strength_for_must_and_penalty_words(self):
        self.assertEqual(classify_strength("必须按时到家，违约罚款200元"), RuleStrength.HARD)

    def test_soft_strength_for_try_and_best_effort_words(self):
        self.assertEqual(classify_strength("尽量接短途单，最好不要绕路"), RuleStrength.SOFT)

    def test_forbidden_categories_extracts_multiple_chinese_quoted_categories(self):
        rules = parse_preference_text("不接“钢材”、“煤炭”类货物")

        self.assertEqual([rule.rule_type for rule in rules], [RuleType.CARGO_CATEGORY, RuleType.CARGO_CATEGORY])
        self.assertEqual([rule.strength for rule in rules], [RuleStrength.HARD, RuleStrength.HARD])
        self.assertEqual(
            [rule.value for rule in rules],
            [{"category": "钢材", "mode": "forbid"}, {"category": "煤炭", "mode": "forbid"}],
        )
        self.assertEqual([rule.source_text for rule in rules], ["不接“钢材”、“煤炭”类货物"] * 2)

    def test_plan_phrase_categories_extracts_one_rule_per_category(self):
        rules = parse_preference_text("不接货源品类为「化工塑料」或「煤炭矿产」的订单。")

        self.assertEqual([rule.rule_type for rule in rules], [RuleType.CARGO_CATEGORY, RuleType.CARGO_CATEGORY])
        self.assertEqual(
            [rule.value for rule in rules],
            [{"category": "化工塑料", "mode": "forbid"}, {"category": "煤炭矿产", "mode": "forbid"}],
        )

    def test_cross_day_no_drive_window(self):
        rule = _only_rule("每天23点至次日6点不接单、不空车赶路")

        self.assertEqual(rule.rule_type, RuleType.NO_DRIVE_WINDOW)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(rule.value, {"start_minute": 1380, "end_minute": 360, "cross_day": True})

    def test_daily_rest_hours(self):
        rule = _only_rule("每天至少有一段连着停车休息满5小时")

        self.assertEqual(rule.rule_type, RuleType.DAILY_REST)
        self.assertEqual(rule.value, {"minutes": 300})

    def test_haul_and_pickup_distance_limits_in_one_text(self):
        rules = parse_preference_text("接货距离不超过20公里，运输距离最多300公里")

        self.assertEqual([rule.rule_type for rule in rules], [RuleType.PICKUP_DISTANCE_LIMIT, RuleType.HAUL_DISTANCE_LIMIT])
        self.assertEqual([rule.value for rule in rules], [{"km": 20.0}, {"km": 300.0}])

    def test_plan_phrase_haul_and_pickup_distance_limits(self):
        rules = parse_preference_text("单笔装卸距离不得超过150公里，赴装货点空驶距离不得超过90公里。")

        self.assertEqual([rule.rule_type for rule in rules], [RuleType.HAUL_DISTANCE_LIMIT, RuleType.PICKUP_DISTANCE_LIMIT])
        self.assertEqual([rule.value for rule in rules], [{"km": 150.0}, {"km": 90.0}])

    def test_monthly_visit_days_coordinate_target_with_radius(self):
        rule = _only_rule("每月至少有2天到坐标(31.2304,121.4737)附近半径10公里")

        self.assertEqual(rule.rule_type, RuleType.MONTHLY_VISIT_DAYS)
        self.assertEqual(rule.value, {"required_days": 2, "lat": 31.2304, "lng": 121.4737, "radius_km": 10.0})

    def test_plan_phrase_monthly_visit_days_coordinate_target_with_radius(self):
        rule = _only_rule("自然月内至少5个不同的自然日到过（23.13，113.26）一公里内。")

        self.assertEqual(rule.rule_type, RuleType.MONTHLY_VISIT_DAYS)
        self.assertEqual(rule.value, {"required_days": 5, "lat": 23.13, "lng": 113.26, "radius_km": 1.0})

    def test_monthly_off_days(self):
        rule = _only_rule("自然月内至少要有2个整天既不接单也不空车乱跑。")

        self.assertEqual(rule.rule_type, RuleType.MONTHLY_OFF_DAYS)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(rule.value, {"required_days": 2})

    def test_real_competition_strong_phrases_are_structured_without_model_fallback(self):
        texts = [
            "我这人熬不住连轴转，每天至少连续停车熄火休息满8小时。",
            "我就在深圳干活，不出市。从 22.54,114.06 这一带出车；跑车或停车时，车辆位置须始终在深圳市范围内（北纬22.42至22.89，东经113.74至114.66）。",
            "自然月内至少要有4个整天不接单。",
            "每天至少有一段连着停车歇满4小时（真熄火歇脚）。",
            "一个月空驶赶路里程总和不得超过100公里；仅对超出部分按公里计罚。",
            "每天凌晨2点至5点不接单、不空车赶路（从发车赶路或去接单时刻计）。",
            "只要这天接了单，首单开工不得晚于当天中午12点。",
            "同一天接单不得超过3单；每多一单按单计罚（无月度封顶）。",
            "每天中午12点至下午1点吃饭歇脚，不接单、不空车赶路。",
            "单笔货装货点至卸货点的距离不得超过100公里。",
            "接单后赴装货点的空驶距离不得超过90公里。",
            "每晚23点至次日早6点不接单、不空车赶路。",
            "自然月内至少放空一整天不接单。",
            "自然月内至少要有2天完全歇着：不接单也不空车乱跑。",
        ]

        rules = parse_preferences(texts)
        unknown_strong_sources = [
            rule.source_text
            for rule in rules
            if rule.rule_type == RuleType.UNKNOWN and rule.strength == RuleStrength.UNKNOWN_STRONG
        ]

        self.assertEqual(unknown_strong_sources, [])

    def test_forbidden_zone(self):
        rule = _only_rule("车辆不得进入以（23.30，113.52）为圆心、半径20公里的区域。")

        self.assertEqual(rule.rule_type, RuleType.FORBIDDEN_ZONE)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(rule.value, {"lat": 23.30, "lng": 113.52, "radius_km": 20.0})

    def test_home_deadline(self):
        rule = _only_rule("每天23点前车辆须在自家位置（23.12，113.28）一公里内。")

        self.assertEqual(rule.rule_type, RuleType.HOME_DEADLINE)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(
            rule.value,
            {"deadline_minute": 1380, "lat": 23.12, "lng": 113.28, "radius_km": 1.0},
        )

    def test_sequence_task(self):
        rule = _only_rule(
            "须先到（23.21，113.37）接上配偶（原地停留不少于10分钟），"
            "再返回老家（23.19，113.36）；须在2026年3月10日22:00前进家门，"
            "到家后须在原处静止，至少待到2026年3月13日22:00。"
        )

        self.assertEqual(rule.rule_type, RuleType.SEQUENCE_TASK)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(
            rule.value,
            {
                "steps": [
                    {"action": "pickup", "lat": 23.21, "lng": 113.37, "target": "spouse", "wait_minutes": 10},
                    {"action": "return_home", "lat": 23.19, "lng": 113.36, "target": "hometown"},
                ],
                "deadline": "2026-03-10 22:00:00",
                "stay_until": "2026-03-13 22:00:00",
            },
        )

    def test_model_fallback_replaces_unknown_strong_rule(self):
        calls = []

        def fake_model_parser(text):
            calls.append(text)
            return {
                "rule_type": "stay_window",
                "strength": "hard",
                "value": {
                    "location": "home",
                    "reason": "sms_notice",
                },
            }

        rules = parse_preferences_with_fallback(["必须按短信通知留在家中。"], fake_model_parser, max_model_calls=1)

        self.assertEqual(calls, ["必须按短信通知留在家中。"])
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.STAY_WINDOW)
        self.assertEqual(rules[0].strength, RuleStrength.HARD)
        self.assertEqual(rules[0].value, {"location": "home", "reason": "sms_notice"})
        self.assertEqual(rules[0].source_text, "必须按短信通知留在家中。")

    def test_model_fallback_accepts_list_of_rule_dicts(self):
        def fake_model_parser(text):
            return [
                {
                    "rule_type": "stay_window",
                    "strength": "hard",
                    "value": {"location": "home"},
                },
                {
                    "rule_type": "home_deadline",
                    "strength": "hard",
                    "value": {"deadline_minute": 1380, "lat": 23.12, "lng": 113.28, "radius_km": 1.0},
                },
            ]

        rules = parse_preferences_with_fallback(["必须按短信通知留在家中。"], fake_model_parser, max_model_calls=1)

        self.assertEqual([rule.rule_type for rule in rules], [RuleType.STAY_WINDOW, RuleType.HOME_DEADLINE])
        self.assertEqual([rule.strength for rule in rules], [RuleStrength.HARD, RuleStrength.HARD])
        self.assertEqual(rules[0].value, {"location": "home"})
        self.assertEqual(
            rules[1].value,
            {"deadline_minute": 1380, "lat": 23.12, "lng": 113.28, "radius_km": 1.0},
        )
        self.assertEqual([rule.source_text for rule in rules], ["必须按短信通知留在家中。"] * 2)

    def test_model_fallback_accepts_rules_wrapper_dict(self):
        def fake_model_parser(text):
            return {
                "rules": [
                    {
                        "rule_type": "stay_window",
                        "strength": "hard",
                        "value": {"location": "home", "reason": "sms_notice"},
                    }
                ]
            }

        rules = parse_preferences_with_fallback(["必须按短信通知留在家中。"], fake_model_parser, max_model_calls=1)

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.STAY_WINDOW)
        self.assertEqual(rules[0].strength, RuleStrength.HARD)
        self.assertEqual(rules[0].value, {"location": "home", "reason": "sms_notice"})
        self.assertEqual(rules[0].source_text, "必须按短信通知留在家中。")

    def test_model_fallback_defaults_missing_strength_to_hard_for_unknown_strong(self):
        def fake_model_parser(text):
            return {
                "rule_type": "stay_window",
                "value": {"location": "home", "reason": "sms_notice"},
            }

        rules = parse_preferences_with_fallback(["必须按短信通知留在家中。"], fake_model_parser, max_model_calls=1)

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.STAY_WINDOW)
        self.assertEqual(rules[0].strength, RuleStrength.HARD)
        self.assertEqual(rules[0].value, {"location": "home", "reason": "sms_notice"})

    def test_model_fallback_does_not_call_model_for_known_rules(self):
        def fail_if_called(text):
            raise AssertionError(f"model parser should not be called for known rule: {text}")

        rules = parse_preferences_with_fallback(["指定熟货源编号240646"], fail_if_called, max_model_calls=1)

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.REQUIRED_CARGO)
        self.assertEqual(rules[0].strength, RuleStrength.HARD)
        self.assertEqual(rules[0].value, {"cargo_id": "240646"})

    def test_model_fallback_does_not_call_model_for_unknown_soft_rules(self):
        def fail_if_called(text):
            raise AssertionError(f"model parser should not be called for unknown soft rule: {text}")

        rules = parse_preferences_with_fallback(["希望下午路线更顺一些"], fail_if_called, max_model_calls=1)

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.UNKNOWN)
        self.assertEqual(rules[0].strength, RuleStrength.UNKNOWN_SOFT)
        self.assertEqual(rules[0].value, {})
        self.assertEqual(rules[0].source_text, "希望下午路线更顺一些")

    def test_model_fallback_preserves_unknown_strong_when_model_fails(self):
        def raise_model_error(text):
            raise RuntimeError("model unavailable")

        rules = parse_preferences_with_fallback(["必须按短信通知留在家中。"], raise_model_error, max_model_calls=1)

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.UNKNOWN)
        self.assertEqual(rules[0].strength, RuleStrength.UNKNOWN_STRONG)
        self.assertEqual(rules[0].value, {})
        self.assertEqual(rules[0].source_text, "必须按短信通知留在家中。")

    def test_model_fallback_preserves_unknown_strong_when_model_payload_is_not_convertible(self):
        def return_unconvertible_payload(text):
            return {"rule_type": "not_a_rule_type", "strength": "hard", "value": {}}

        rules = parse_preferences_with_fallback(
            ["必须按短信通知留在家中。"],
            return_unconvertible_payload,
            max_model_calls=1,
        )

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.UNKNOWN)
        self.assertEqual(rules[0].strength, RuleStrength.UNKNOWN_STRONG)
        self.assertEqual(rules[0].value, {})
        self.assertEqual(rules[0].source_text, "必须按短信通知留在家中。")

    def test_required_cargo_id(self):
        rule = _only_rule("指定熟货源编号240646")

        self.assertEqual(rule.rule_type, RuleType.REQUIRED_CARGO)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(rule.value, {"cargo_id": "240646"})

    def test_unparsed_strong_marker_becomes_unknown_strong(self):
        rule = _only_rule("必须按短信通知留在家中。")

        self.assertEqual(rule.rule_type, RuleType.UNKNOWN)
        self.assertEqual(rule.strength, RuleStrength.UNKNOWN_STRONG)
        self.assertEqual(rule.value, {})

    def test_unparsed_soft_text_becomes_unknown_soft(self):
        rule = _only_rule("希望下午路线更顺一些")

        self.assertEqual(rule.rule_type, RuleType.UNKNOWN)
        self.assertEqual(rule.strength, RuleStrength.UNKNOWN_SOFT)

    def test_parse_preferences_caches_and_deduplicates_by_text(self):
        preference = {"text": "指定熟货源编号240646"}

        rules = parse_preferences([preference, preference, {"preference": "指定熟货源编号240646"}])

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.REQUIRED_CARGO)
        self.assertEqual(rules[0].value, {"cargo_id": "240646"})
        self.assertEqual(rules[0].source_text, "指定熟货源编号240646")

    def test_parse_preference_text_returns_fresh_mutable_lists(self):
        first = parse_preference_text("指定熟货源编号240646")
        first.append(PreferenceRule(RuleType.UNKNOWN, RuleStrength.UNKNOWN_SOFT, {}, "mutated"))

        second = parse_preference_text("指定熟货源编号240646")

        self.assertEqual(len(second), 1)
        self.assertEqual(second[0].value, {"cargo_id": "240646"})

    def test_parse_preference_text_returns_fresh_nested_value_dicts(self):
        text = (
            "须先到（23.21，113.37）接上配偶（原地停留不少于10分钟），"
            "再返回老家（23.19，113.36）；须在2026年3月10日22:00前进家门，"
            "到家后须在原处静止，至少待到2026年3月13日22:00。"
        )
        first = parse_preference_text(text)
        first[0].value["steps"][0]["wait_minutes"] = 99
        first[0].value["deadline"] = "mutated"

        second = parse_preference_text(text)

        self.assertEqual(second[0].value["steps"][0]["wait_minutes"], 10)
        self.assertEqual(second[0].value["deadline"], "2026-03-10 22:00:00")


if __name__ == "__main__":
    unittest.main()
