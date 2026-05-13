from __future__ import annotations

import unittest

from preference_parser import classify_strength, parse_preference_text, parse_preferences
from preference_rules import PlannedIntent, RuleStrength, RuleType


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
        rule = _only_rule("不接“钢材”、“煤炭”类货物")

        self.assertEqual(rule.rule_type, RuleType.CARGO_CATEGORY)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(rule.source_text, "不接“钢材”、“煤炭”类货物")
        self.assertEqual(rule.value["forbidden_categories"], ["钢材", "煤炭"])

    def test_cross_day_no_drive_window(self):
        rules = parse_preference_text("每天23点至次日6点不接单、不空车赶路")

        self.assertEqual(len(rules), 1)
        rule = rules[0]
        self.assertEqual(rule.rule_type, RuleType.NO_DRIVE_WINDOW)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(rule.value["start_minute"], 23 * 60)
        self.assertEqual(rule.value["end_minute"], 6 * 60)
        self.assertTrue(rule.value["cross_day"])
        self.assertEqual(rule.value["restrictions"], ["no_order", "no_deadhead"])

    def test_daily_rest_hours(self):
        rule = _only_rule("每天至少有一段连着停车休息满5小时")

        self.assertEqual(rule.rule_type, RuleType.DAILY_REST)
        self.assertEqual(rule.value["minutes"], 300)
        self.assertTrue(rule.value["continuous"])

    def test_haul_and_pickup_distance_limits_in_one_text(self):
        rules = parse_preference_text("接货距离不超过20公里，运输距离最多300公里")

        self.assertEqual([rule.rule_type for rule in rules], [RuleType.PICKUP_DISTANCE_LIMIT, RuleType.HAUL_DISTANCE_LIMIT])
        self.assertEqual([rule.value["max_km"] for rule in rules], [20, 300])

    def test_monthly_visit_days_coordinate_target_with_radius(self):
        rule = _only_rule("每月至少有2天到坐标(31.2304,121.4737)附近半径10公里")

        self.assertEqual(rule.rule_type, RuleType.MONTHLY_VISIT_DAYS)
        self.assertEqual(rule.value["min_days"], 2)
        self.assertEqual(rule.value["lat"], 31.2304)
        self.assertEqual(rule.value["lng"], 121.4737)
        self.assertEqual(rule.value["radius_km"], 10)

    def test_required_cargo_id(self):
        rule = _only_rule("指定熟货源编号240646")

        self.assertEqual(rule.rule_type, RuleType.REQUIRED_CARGO)
        self.assertEqual(rule.strength, RuleStrength.HARD)
        self.assertEqual(rule.value["cargo_id"], "240646")

    def test_parse_preferences_caches_and_deduplicates_by_text(self):
        preference = {"text": "指定熟货源编号240646"}

        rules = parse_preferences([preference, preference, {"preference": "指定熟货源编号240646"}])

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_type, RuleType.REQUIRED_CARGO)
        self.assertEqual(rules[0].value, {"cargo_id": "240646"})
        self.assertEqual(rules[0].source_text, "指定熟货源编号240646")
        self.assertIs(parse_preference_text("指定熟货源编号240646"), parse_preference_text("指定熟货源编号240646"))


if __name__ == "__main__":
    unittest.main()
