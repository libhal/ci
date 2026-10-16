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
Computes the next release of one version line of a repository.

A version line is one major version that lives in its own directory (e.g.
4.x.y in v4/). The line only looks at its own tags and at commits that change
its directory.

  1. The line's last release is its newest <major>.X.Y tag. Until one exists,
     it is the newest <major>.0.0-alpha.K tag instead. A line with neither is
     not started yet; major versions are started by hand.
  2. The subject lines of the commits since that tag that change the
     directory are scanned for (minor) and (patch). The highest one wins:
       - released line:     (minor) -> <major>.X+1.0, (patch) -> <major>.X.Y+1
       - pre-release line:  either -> <major>.0.0-alpha.K+1
  3. (major) is an error: a commit can't start a major version.

A commit that changes several directories counts for each of their lines.
Only subject lines count, so a commit body can mention the keywords (e.g. a
squash merge listing its commits, or a message describing these rules).

Prints the result as key=value lines, or appends them to the file given with
--output (e.g. $GITHUB_OUTPUT):

    tag=4.3.0          (empty when there is nothing to release)
    previous=4.2.7     (the tag the release notes start from)
    prerelease=false

Usage:
    python3 semantic_release.py --major 4 --dir v4
    python3 semantic_release.py --major 4 --dir v4 --output "$GITHUB_OUTPUT"
"""

import argparse
import re
import subprocess
import sys

KEYWORD = re.compile(r"\((major|minor|patch)\)")


class ReleaseError(Exception):
    pass


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True,
                          text=True).stdout


def last_release(major: int) -> tuple[str, bool] | None:
    """Returns (tag, is_prerelease) for the line's newest tag, or None."""
    releases = []
    alphas = []
    for tag in git("tag", "--list", f"{major}.*").split():
        if match := re.fullmatch(rf"{major}\.(\d+)\.(\d+)", tag):
            releases.append((int(match[1]), int(match[2]), tag))
        elif match := re.fullmatch(rf"{major}\.0\.0-alpha\.(\d+)", tag):
            alphas.append((int(match[1]), tag))
    if releases:
        return max(releases)[-1], False
    if alphas:
        return max(alphas)[-1], True
    return None


def keywords_since(tag: str, directory: str, ref: str) -> set[str]:
    """Returns the release keywords in the subject lines of commits after
    `tag` that change `directory`."""
    log = git("log", "--format=%H %s", f"{tag}..{ref}", "--", directory)
    found = set()
    for line in log.splitlines():
        commit, _, subject = line.partition(" ")
        words = set(KEYWORD.findall(subject))
        if "major" in words:
            raise ReleaseError(
                f"commit {commit[:12]} asks for a (major) release. Major "
                "versions are started by hand: publish the first tag of the "
                "new line yourself. Remove (major) from the commit subject.")
        found |= words
    return found


def next_release(major: int, directory: str, ref: str = "HEAD") -> dict:
    """Returns {"tag", "previous", "prerelease"}; "tag" is empty when there
    is nothing to release."""
    nothing = {"tag": "", "previous": "", "prerelease": False}

    last = last_release(major)
    if last is None:
        print(f"No {major}.* tag yet, so the {major}.x line isn't started. "
              f"Publish {major}.0.0-alpha.1 or {major}.0.0 by hand to start "
              "it.", file=sys.stderr)
        return nothing
    previous, prerelease = last

    words = keywords_since(previous, directory, ref)
    if not words:
        print(f"No commit since {previous} that changes {directory} asks "
              "for a release.", file=sys.stderr)
        return nothing

    if prerelease:
        alpha = int(previous.rsplit(".", 1)[1])
        tag = f"{major}.0.0-alpha.{alpha + 1}"
    else:
        _, minor, patch = (int(part) for part in previous.split("."))
        if "minor" in words:
            tag = f"{major}.{minor + 1}.0"
        else:
            tag = f"{major}.{minor}.{patch + 1}"
    return {"tag": tag, "previous": previous, "prerelease": prerelease}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--major", type=int, required=True,
                        help="Major version of the line, e.g. 4")
    parser.add_argument("--dir", required=True,
                        help="Directory of the line, e.g. v4 (or .)")
    parser.add_argument("--ref", default="HEAD",
                        help="Commit to release (default: HEAD)")
    parser.add_argument("--output",
                        help="Append the result to this file instead of "
                        "printing it")
    args = parser.parse_args()

    try:
        result = next_release(args.major, args.dir, args.ref)
    except ReleaseError as error:
        print(f"::error::{error}")
        return 1

    lines = (f"tag={result['tag']}\n"
             f"previous={result['previous']}\n"
             f"prerelease={str(result['prerelease']).lower()}\n")
    if args.output:
        with open(args.output, "a", encoding="utf-8") as output:
            output.write(lines)
    print(lines, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
