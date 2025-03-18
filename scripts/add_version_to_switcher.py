#!/usr/bin/env python3
import json
import os
import re
import sys


def add_version_to_switcher(version, url):
    """
    Add a version to the docs/switcher.json file.

    Args:
        version (str): The version to add (e.g., "4.11.8")
    """
    # If this is a versioned release (contains digits)
    if not re.search(r"\d", version):
        print("Not a versioned release, skipping switcher.json update")
        return

    # Read the existing switcher.json if it exists
    switcher_file = "docs/switcher.json"
    switcher_data = []

    if os.path.exists(switcher_file):
        with open(switcher_file, "r") as f:
            switcher_data = json.load(f)

    # Check if version already exists
    version_exists = False
    for item in switcher_data:
        if item["version"] == version:
            version_exists = True
            break

    # Add new version if it doesn't exist
    if not version_exists:
        new_entry = {
            "name": version,
            "version": version,
            "url": f"{url}/{version}/"
        }

        # Add the new entry
        switcher_data.append(new_entry)

        # Sort entries: "main" first, then by version number in descending order
        def sort_key(item):
            if item["version"] == "main":
                return "0"  # Ensure main is first
            return item["version"]

        switcher_data.sort(key=sort_key)

        # Write the updated JSON back
        os.makedirs(os.path.dirname(switcher_file), exist_ok=True)
        with open(switcher_file, "w") as f:
            json.dump(switcher_data, f, indent=2)
        print(f"Added version {version} to switcher.json")
    else:
        print(f"Version {version} already exists in switcher.json, skipping")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        add_version_to_switcher(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python add_version_to_switcher.py VERSION URL")
        sys.exit(1)
