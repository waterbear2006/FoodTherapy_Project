import asyncio
import unittest

from Backened.core.engines.daily_report_engine import DailyReportEngine


class DailyReportEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = DailyReportEngine()

    def test_generate_daily_report_basic(self):
        payload = asyncio.run(
            self.engine.get_daily_report(
                user_id="test_user_1",
                constitution_vector={
                    "阴虚质": 80,
                    "湿热质": 30,
                    "气虚质": 20,
                },
                available_ingredients=["西红柿", "鸡蛋"],
                force_refresh=True,
            )
        )

        self.assertEqual(payload["user_id"], "test_user_1")
        self.assertEqual(payload["primary_constitution"], "阴虚质")
        self.assertIn("constitution_delta", payload)
        self.assertIn("matched_tags", payload)
        self.assertIn("recommended_recipe_ids", payload)
        self.assertIn("recommended_recipes", payload)
        self.assertIn("report_text", payload)
        self.assertIn("solar_term", payload)
        self.assertIn("season", payload)
        self.assertIn("ui_card", payload)
        self.assertFalse(payload["cache_hit"])
        self.assertGreater(len(payload["recommended_recipes"]), 0)

    def test_daily_idempotency_cache(self):
        first = asyncio.run(
            self.engine.get_daily_report(
                user_id="test_user_2",
                constitution_vector={
                    "阴虚质": 70,
                    "湿热质": 40,
                },
                available_ingredients=["枸杞"],
                force_refresh=False,
            )
        )
        second = asyncio.run(
            self.engine.get_daily_report(
                user_id="test_user_2",
                constitution_vector={
                    "阴虚质": 90,  # 即使变化，同日请求也应命中缓存
                    "湿热质": 10,
                },
                available_ingredients=["冬瓜"],
                force_refresh=False,
            )
        )

        self.assertFalse(first["cache_hit"])
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["date"], second["date"])
        self.assertEqual(first["recommended_recipe_ids"], second["recommended_recipe_ids"])


if __name__ == "__main__":
    unittest.main()
