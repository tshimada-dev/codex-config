from __future__ import annotations
import os
import sys
import tempfile
import unittest
from pathlib import Path

WORK=Path(sys.argv.pop(1)).resolve()
sys.path.insert(0,str(WORK))
from src.cache_cleanup import reset_cache


class Hidden(unittest.TestCase):
    def test_all_owned_dirs_exist_and_are_empty(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in ("compiled","tmp","reports"):
                p=root/name; p.mkdir(); (p/"old").write_text("x")
            reset_cache(root)
            for name in ("compiled","tmp","reports"):
                self.assertTrue((root/name).is_dir())
                self.assertEqual(list((root/name).iterdir()),[])

    def test_foreign_child_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"sdk").mkdir(); marker=root/"sdk"/"keep"; marker.write_text("keep")
            reset_cache(root)
            self.assertEqual(marker.read_text(),"keep")

    def test_symlink_owned_path_does_not_delete_target(self):
        if not hasattr(os,"symlink"):
            self.skipTest("symlink unsupported")
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as target_d:
            root=Path(d); target=Path(target_d)
            marker=target/"keep"; marker.write_text("keep")
            try:
                os.symlink(target, root/"reports", target_is_directory=True)
            except OSError:
                self.skipTest("symlink creation unavailable")
            reset_cache(root)
            self.assertEqual(marker.read_text(),"keep")
            self.assertTrue((root/"reports").is_dir())
            self.assertFalse((root/"reports").is_symlink())


if __name__ == "__main__":
    unittest.main()
