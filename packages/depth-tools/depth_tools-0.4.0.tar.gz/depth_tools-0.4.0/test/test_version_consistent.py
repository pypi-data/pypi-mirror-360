import re
import unittest
from pathlib import Path

import depth_tools


class TestVersionConsistent(unittest.TestCase):
    def test_toml_version(self):
        toml_version_str = self.get_toml_version()
        reported_version_str = depth_tools.__version__

        self.assertEqual(toml_version_str, reported_version_str)

    def get_toml_version(self) -> str:
        toml_path = Path(__file__).parent.parent / "pyproject.toml"

        toml_data = toml_path.read_text()

        # tomllib is only available for python 3.11+
        toml_version_str_candidates = re.findall(
            r"\bversion\s*=\s*\"(\d+\.\d+\.\d+)\"", toml_data
        )

        if len(toml_version_str_candidates) != 1:
            self.fail("Exactly one version should be found in pyproject.toml")

        return toml_version_str_candidates[0]
