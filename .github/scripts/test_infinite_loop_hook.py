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

"""Tests for the no-continue-infinite-loop hook in .pre-commit-hooks.yaml.

The pattern is compiled the way pre-commit's pygrep compiles it with
--multiline, so these tests need neither pre-commit nor PyYAML.
"""

import pathlib
import re
import unittest

HOOKS = pathlib.Path(__file__).resolve().parents[2] / ".pre-commit-hooks.yaml"


def hook_field(name):
    """Return a field of the no-continue-infinite-loop hook, as text."""
    lines = HOOKS.read_text().splitlines()
    start = lines.index("- id: no-continue-infinite-loop")
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("- id:"):
            break
        if not line.startswith(f"  {name}:"):
            continue
        value = line.split(":", 1)[1].strip()
        if value != "|":
            return value
        block = []
        for body in lines[index + 1:]:
            if body.strip() and not body.startswith("    "):
                break
            block.append(body[4:])
        return "\n".join(block) + "\n"
    raise KeyError(name)


PATTERN = re.compile(hook_field("entry").encode(), re.MULTILINE | re.DOTALL)

# Each of these compiles to nothing with Clang.
DELETED = {
    "while, braces": "while (true) { continue; }",
    "while, no braces": "while (true) continue;",
    "while (1)": "while (1) {\n  continue;\n}",
    "while (10)": "while (10) { continue; }",
    "while (1U)": "while (1U) { continue; }",
    "no spaces": "while(true){continue;}",
    "for (;;)": "for (;;) {\n  continue;\n}",
    "for with spaces": "for ( ; ; ) { continue; }",
    "do while": "do {\n  continue;\n} while (true);",
    "line comment first": (
        "while (true) {\n"
        "  // halt here and wait for a debugger to connect\n"
        "  continue;\n"
        "}"
    ),
    "block comment first": "while (true) { /* spin */ continue; }",
    "line comment last": "while (true) {\n  continue;  // spin\n}",
}

# Clang keeps each of these: an empty body, a body with a side effect, or a
# condition that isn't a constant.
KEPT = {
    "empty body": "while (true) {}",
    "comment only": "while (true) {\n  // Halt here forever.\n}",
    "empty for": "for (;;) {\n}",
    "polling a register": (
        "while (hal::bit_extract<state>(reg->status) == states::busy) {\n"
        "  continue;\n"
        "}"
    ),
    "polling a variable": "while (status == 0) { continue; }",
    "work then continue": "while (true) {\n  work();\n  continue;\n}",
    "continue in an if": "while (true) {\n  if (done) { continue; }\n  work();\n}",
    "do while with work": "do { work(); continue; } while (true);",
    "do while polling": "do { continue; } while (status == 0);",
}

# Text that only looks like one of the deleted loops.
LOOKALIKES = {
    "identifier ending in while": "somewhile (true) { continue; }",
    "identifier ending in for": "platform(;;) { continue; }",
    "variable starting with continue": "while (true) { continue_count++; }",
    "while (0)": "while (0) { continue; }",
}


class InfiniteLoopHookTest(unittest.TestCase):
    def test_runs_on_whole_files(self):
        self.assertIn("--multiline", hook_field("args"))

    def test_loops_clang_deletes_are_found(self):
        for name, code in DELETED.items():
            with self.subTest(name):
                self.assertIsNotNone(PATTERN.search(code.encode()))

    def test_loops_clang_keeps_are_not_found(self):
        for name, code in (KEPT | LOOKALIKES).items():
            with self.subTest(name):
                self.assertIsNone(PATTERN.search(code.encode()))

    def test_finds_the_loop_in_a_function(self):
        code = (
            "void wait_forever()\n"
            "{\n"
            "  while (true) {}\n"
            "}\n"
            "\n"
            "void halt()\n"
            "{\n"
            "  while (true) {\n"
            "    continue;\n"
            "  }\n"
            "}\n"
        ).encode()
        match = PATTERN.search(code)
        self.assertIsNotNone(match)
        self.assertEqual(code[: match.start()].count(b"\n") + 1, 8)

    def test_checks_cpp_and_module_files_only(self):
        files = re.compile(hook_field("files"))
        for name in ["a.cpp", "a.cppm", "a.hpp", "a.h", "a.c", "a.ipp"]:
            with self.subTest(name):
                self.assertIsNotNone(files.search(name))
        for name in ["a.md", "a.py", "a.txt", "CMakeLists.txt"]:
            with self.subTest(name):
                self.assertIsNone(files.search(name))


if __name__ == "__main__":
    unittest.main()
