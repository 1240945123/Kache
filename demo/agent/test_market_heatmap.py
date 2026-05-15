from __future__ import annotations

import unittest

from market_heatmap import MarketHeatmap


def _cargo(cargo_id, create_minute, lat, lng, price=500.0):
    return {
        "cargo_id": cargo_id,
        "create_minute": create_minute,
        "price": price,
        "start": {"lat": lat, "lng": lng},
    }


class MarketHeatmapTest(unittest.TestCase):
    def test_future_value_counts_nearby_future_cargo(self):
        heatmap = MarketHeatmap.from_cargo_records(
            [
                _cargo("NEAR1", 120, 23.01, 113.01, price=500.0),
                _cargo("NEAR2", 180, 23.04, 113.02, price=700.0),
                _cargo("FAR", 140, 25.0, 115.0, price=900.0),
            ]
        )

        value = heatmap.future_value(23.0, 113.0, current_minute=100, horizon_minutes=120)

        self.assertGreater(value, 0.0)
        self.assertLessEqual(value, 500.0)

    def test_future_value_ignores_past_and_out_of_horizon_cargo(self):
        heatmap = MarketHeatmap.from_cargo_records(
            [
                _cargo("PAST", 90, 23.01, 113.01),
                _cargo("LATE", 400, 23.01, 113.01),
            ]
        )

        self.assertEqual(heatmap.future_value(23.0, 113.0, current_minute=100, horizon_minutes=120), 0.0)


if __name__ == "__main__":
    unittest.main()
