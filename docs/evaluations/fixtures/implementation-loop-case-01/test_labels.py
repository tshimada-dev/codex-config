import unittest

from labels import normalize_priority


class NormalizePriorityTests(unittest.TestCase):
    def test_normalizes_supported_priority(self):
        self.assertEqual("P2", normalize_priority(" p2 "))

    def test_rejects_non_string(self):
        self.assertIsNone(normalize_priority(2))


if __name__ == "__main__":
    unittest.main()
