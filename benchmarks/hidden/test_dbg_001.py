from __future__ import annotations
import sys
import unittest
from pathlib import Path

WORK = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(WORK))
from src.cache import Cache


class Hidden(unittest.TestCase):
    def make(self):
        c=Cache()
        c.put("a", 1, expires_at=20, stale_until=30)
        return c

    def test_exact_expiry_is_stale_and_requests_refresh(self):
        c=self.make()
        out=c.get("a", now=20)
        self.assertEqual((out.value,out.state,out.request_refresh),(1,"stale",True))
        self.assertEqual(c.metrics,{"hit":0,"miss":0,"stale":1})

    def test_inside_stale_window(self):
        c=self.make()
        out=c.get("a", now=29.999)
        self.assertEqual((out.value,out.state,out.request_refresh),(1,"stale",True))
        self.assertEqual(c.metrics,{"hit":0,"miss":0,"stale":1})

    def test_exact_stale_until_is_miss(self):
        c=self.make()
        out=c.get("a", now=30)
        self.assertEqual((out.value,out.state,out.request_refresh),(None,"miss",False))
        self.assertEqual(c.metrics,{"hit":0,"miss":1,"stale":0})

    def test_fresh_never_requests_refresh(self):
        c=self.make()
        out=c.get("a", now=19.999)
        self.assertFalse(out.request_refresh)
        self.assertEqual(c.metrics["hit"],1)


if __name__ == "__main__":
    unittest.main()
