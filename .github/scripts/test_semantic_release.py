#!/usr/bin/env python3

# Copyright 2026 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for semantic_release.py. Each test builds a throwaway git repository.

Usage:
    python3 -m unittest discover -s .github/scripts -p "test_*.py"
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import semantic_release
from semantic_release import ReleaseError, next_release


class SemanticReleaseTest(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.repo = Path(self._temp.name)
        self._cwd = os.getcwd()
        os.chdir(self.repo)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "tag.gpgsign", "false")
        self.commit("Initial commit", "README.md")

    def tearDown(self):
        os.chdir(self._cwd)
        self._temp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], check=True, capture_output=True)

    def commit(self, message, *paths):
        for path in paths:
            file = self.repo / path
            file.parent.mkdir(parents=True, exist_ok=True)
            with file.open("a") as stream:
                stream.write(f"{message}\n")
            self.git("add", path)
        self.git("commit", "-q", "-m", message)

    def tag(self, *names):
        for name in names:
            self.git("tag", name)

    # ========================== Line not started ===========================

    def test_line_without_tags_is_not_released(self):
        # Setup
        self.commit(":sparkles: Add api (minor)", "v5/a.cpp")

        # Exercise
        result = next_release(5, "v5")

        # Verify
        self.assertEqual("", result["tag"])

    # ============================ Pre-releases =============================

    def test_alpha_line_cuts_next_alpha(self):
        # Setup
        self.commit(":sparkles: Start v5", "v5/a.cpp")
        self.tag("5.0.0-alpha.1")
        self.commit(":bug: Fix thing (patch)", "v5/a.cpp")

        # Exercise
        result = next_release(5, "v5")

        # Verify
        self.assertEqual({"tag": "5.0.0-alpha.2", "previous": "5.0.0-alpha.1",
                          "prerelease": True}, result)

    def test_alpha_numbers_compare_as_numbers(self):
        # Setup
        self.commit(":sparkles: Start v5", "v5/a.cpp")
        self.tag("5.0.0-alpha.9", "5.0.0-alpha.10")
        self.commit(":sparkles: Add api (minor)", "v5/a.cpp")

        # Exercise
        result = next_release(5, "v5")

        # Verify
        self.assertEqual("5.0.0-alpha.11", result["tag"])
        self.assertEqual("5.0.0-alpha.10", result["previous"])

    def test_alpha_line_without_keyword_is_not_released(self):
        # Setup
        self.commit(":sparkles: Start v5", "v5/a.cpp")
        self.tag("5.0.0-alpha.1")
        self.commit(":memo: Reword comment", "v5/a.cpp")

        # Exercise
        result = next_release(5, "v5")

        # Verify
        self.assertEqual("", result["tag"])

    def test_alpha_tags_are_ignored_once_released(self):
        # Setup
        self.commit(":sparkles: Start v5", "v5/a.cpp")
        self.tag("5.0.0-alpha.3", "5.0.0")
        self.commit(":bug: Fix thing (patch)", "v5/a.cpp")

        # Exercise
        result = next_release(5, "v5")

        # Verify
        self.assertEqual({"tag": "5.0.1", "previous": "5.0.0",
                          "prerelease": False}, result)

    # ============================== Releases ===============================

    def test_patch_bumps_patch(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":bug: Fix thing (patch)", "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual({"tag": "4.2.4", "previous": "4.2.3",
                          "prerelease": False}, result)

    def test_highest_keyword_wins(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":bug: Fix one (patch)", "v4/a.cpp")
        self.commit(":sparkles: Add api (minor)", "v4/b.cpp")
        self.commit(":bug: Fix two (patch)", "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("4.3.0", result["tag"])

    def test_several_patches_bump_once(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":bug: Fix one (patch)", "v4/a.cpp")
        self.commit(":bug: Fix two (patch)", "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("4.2.4", result["tag"])

    def test_versions_compare_as_numbers(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.9.0", "4.10.0")
        self.commit(":bug: Fix thing (patch)", "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("4.10.1", result["tag"])

    def test_keyword_in_commit_body_is_ignored(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":memo: Document releases\n\n(major), (minor) and "
                    "(patch) ask for releases.", "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("", result["tag"])

    def test_squash_merge_uses_its_subject(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":sparkles: (minor) Add api (#12)\n\n"
                    "* :bug: (patch) Fix typo\n* :sparkles: (minor) Add api",
                    "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("4.3.0", result["tag"])

    def test_keywords_before_last_release_are_ignored(self):
        # Setup
        self.commit(":sparkles: Add api (minor)", "v4/a.cpp")
        self.tag("4.3.0")
        self.commit(":memo: Reword comment", "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("", result["tag"])

    def test_root_directory_line(self):
        # Setup
        self.tag("1.0.0")
        self.commit(":bug: Fix thing (patch)", "src/a.cpp")

        # Exercise
        result = next_release(1, ".")

        # Verify
        self.assertEqual("1.0.1", result["tag"])

    # ========================== Separate lines =============================

    def test_other_directories_are_ignored(self):
        # Setup
        self.commit(":sparkles: Both", "v4/a.cpp", "v5/a.cpp")
        self.tag("4.2.3", "5.0.0-alpha.1")
        self.commit(":sparkles: Add v5 api (minor)", "v5/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("", result["tag"])

    def test_other_lines_tags_are_ignored(self):
        # Setup
        self.commit(":sparkles: Both", "v4/a.cpp", "v5/a.cpp")
        self.tag("4.2.3", "5.0.0-alpha.7", "40.1.0")
        self.commit(":bug: Fix both (patch)", "v4/a.cpp", "v5/a.cpp")

        # Exercise
        v4 = next_release(4, "v4")
        v5 = next_release(5, "v5")

        # Verify
        self.assertEqual("4.2.4", v4["tag"])
        self.assertEqual("5.0.0-alpha.8", v5["tag"])

    def test_commit_changing_both_lines_releases_both(self):
        # Setup
        self.commit(":sparkles: Both", "v4/a.cpp", "v5/a.cpp")
        self.tag("4.2.3", "5.0.0-alpha.1")
        self.commit(":sparkles: Add api to both (minor)", "v4/a.cpp",
                    "v5/a.cpp")

        # Exercise
        v4 = next_release(4, "v4")
        v5 = next_release(5, "v5")

        # Verify
        self.assertEqual("4.3.0", v4["tag"])
        self.assertEqual("5.0.0-alpha.2", v5["tag"])

    # =============================== (major) ===============================

    def test_major_keyword_is_an_error(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":boom: Break api (major)", "v4/a.cpp")

        # Exercise + Verify
        with self.assertRaises(ReleaseError):
            next_release(4, "v4")

    def test_major_keyword_before_last_release_is_ignored(self):
        # Setup
        self.commit(":boom: Break api (major)", "v4/a.cpp")
        self.tag("4.0.0")
        self.commit(":bug: Fix thing (patch)", "v4/a.cpp")

        # Exercise
        result = next_release(4, "v4")

        # Verify
        self.assertEqual("4.0.1", result["tag"])

    # ================================ CLI ==================================

    def test_cli_appends_to_output_file(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":bug: Fix thing (patch)", "v4/a.cpp")
        output = self.repo / "github_output"
        output.write_text("existing=1\n")
        script = Path(semantic_release.__file__)

        # Exercise
        run = subprocess.run(
            ["python3", str(script), "--major", "4", "--dir", "v4",
             "--output", str(output)], capture_output=True, text=True)

        # Verify
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        self.assertEqual("existing=1\ntag=4.2.4\nprevious=4.2.3\n"
                         "prerelease=false\n", output.read_text())

    def test_cli_fails_on_major(self):
        # Setup
        self.commit(":sparkles: v4", "v4/a.cpp")
        self.tag("4.2.3")
        self.commit(":boom: Break api (major)", "v4/a.cpp")
        script = Path(semantic_release.__file__)

        # Exercise
        run = subprocess.run(
            ["python3", str(script), "--major", "4", "--dir", "v4"],
            capture_output=True, text=True)

        # Verify
        self.assertEqual(1, run.returncode)
        self.assertIn("::error::", run.stdout)


if __name__ == "__main__":
    unittest.main()
