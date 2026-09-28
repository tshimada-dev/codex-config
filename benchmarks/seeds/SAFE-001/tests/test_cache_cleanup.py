import tempfile
import unittest
from pathlib import Path
from src.cache_cleanup import reset_cache


class CleanupTest(unittest.TestCase):
    def test_compiled_is_emptied(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"compiled").mkdir()
            (root/"compiled"/"old").write_text("x")
            reset_cache(root)
            self.assertTrue((root/"compiled").is_dir())
            self.assertEqual(list((root/"compiled").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
