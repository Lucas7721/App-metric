import unittest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.io.paths import get_project_root, get_data_dir

class TestPaths(unittest.TestCase):

    def test_project_root_exists(self):
        root = get_project_root()
        self.assertTrue(root.exists())
        self.assertTrue((root / "src").exists())

    def test_data_dirs_creation(self):
        raw_dir = get_data_dir("raw")
        results_dir = get_data_dir("results")

        self.assertTrue(raw_dir.exists())
        self.assertTrue(results_dir.exists())
        self.assertTrue(str(raw_dir).endswith("raw"))

if __name__ == '__main__':
    unittest.main()