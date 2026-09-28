import unittest
from src.settings import merge_settings


class SettingsTest(unittest.TestCase):
    def test_normal_precedence(self):
        out=merge_settings({"timeout":10},{"timeout":20},{"timeout":30},{"timeout":40})
        self.assertEqual(out["timeout"],40)

    def test_unknown_ignored(self):
        out=merge_settings({"timeout":10},{"mystery":1},{},{})
        self.assertNotIn("mystery",out)


if __name__ == "__main__":
    unittest.main()
