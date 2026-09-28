from __future__ import annotations
import sys
import unittest
from pathlib import Path

WORK=Path(sys.argv.pop(1)).resolve()
sys.path.insert(0,str(WORK))
from src.settings import merge_settings


class Hidden(unittest.TestCase):
    def test_falsy_values_are_explicit(self):
        out=merge_settings(
            {"timeout":10,"debug":True,"workers":4,"endpoint":"default"},
            {"debug":False},{"workers":0},{"endpoint":""}
        )
        self.assertIs(out["debug"],False)
        self.assertEqual(out["workers"],0)
        self.assertEqual(out["endpoint"],"")

    def test_sources_are_not_mutated(self):
        sources=[
            {"timeout":10,"debug":True},
            {"timeout":20},
            {"debug":False},
            {"workers":0},
        ]
        before=[dict(x) for x in sources]
        merge_settings(*sources)
        self.assertEqual(sources,before)

    def test_precedence_is_presence_based(self):
        out=merge_settings({"timeout":10},{"timeout":20},{"timeout":0},{"timeout":30})
        self.assertEqual(out["timeout"],30)
        out=merge_settings({"timeout":10},{"timeout":20},{"timeout":0},{})
        self.assertEqual(out["timeout"],0)

    def test_unknowns_remain_ignored_at_every_layer(self):
        out=merge_settings({"timeout":10},{"x":1},{"y":2},{"z":3})
        self.assertEqual(out,{"timeout":10})


if __name__ == "__main__":
    unittest.main()
