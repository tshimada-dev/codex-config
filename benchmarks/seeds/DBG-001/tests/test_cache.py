import unittest
from src.cache import Cache


class CacheTest(unittest.TestCase):
    def test_fresh(self):
        c = Cache()
        c.put("a", 1, expires_at=20, stale_until=30)
        out = c.get("a", now=19)
        self.assertEqual((out.value, out.state), (1, "fresh"))
        self.assertEqual(c.metrics, {"hit": 1, "miss": 0, "stale": 0})

    def test_missing(self):
        c = Cache()
        self.assertEqual(c.get("x", now=1).state, "miss")


if __name__ == "__main__":
    unittest.main()
