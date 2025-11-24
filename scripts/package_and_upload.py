#!/usr/bin/env python3
# Copyright 2024 - 2025 Khalil Estell and the libhal contributors
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

import argparse
import os
import subprocess
import sys


def run_command(cmd, description, input_data=None):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    result = subprocess.run(
        cmd,
        input=input_data.encode() if input_data else None,
        check=False
    )
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        sys.exit(1)
    return result


def add_remotes(remote_urls):
    """Add conan remotes from comma-separated list"""
    if not remote_urls:
        return

    urls = [url.strip() for url in remote_urls.split(",") if url.strip()]
    for i, url in enumerate(urls):
        remote_name = "remote-package-repo" if i == 0 else f"remote-{i}"
        run_command(
            ["conan", "remote", "add", remote_name, url],
            f"📡 Add conan remote '{remote_name}': {url}"
        )


def install_settings_yml(settings_yml_url, settings_yml_path):
    """Install libhal settings_user.yml if provided"""
    if not settings_yml_url:
        return

    run_command(
        ["conan", "config", "install", "-sf",
         settings_yml_path, settings_yml_url],
        "📡 Install libhal settings_user.yml"
    )


def create_package(args, build_type):
    """Create a single conan package"""
    cmd = [
        "conan", "create", args.dir,
        "-s:h", f"build_type={build_type}",
        "-pr:h", args.compiler_profile,
        "-s:h", f"os={args.os}",
        "-s:h", f"arch={args.arch}",
        "--version", args.version
    ]

    run_command(cmd, f"📦 Create '{build_type}' package")


def upload_packages(args):
    """Upload packages to remote repository"""
    if args.version == "latest":
        print("ℹ️  Skipping upload for version 'latest'")
        return

    user = os.environ.get("CONAN_REMOTE_USER")
    password = os.environ.get("CONAN_REMOTE_PASSWORD")

    if not user or not password:
        print("❌ Missing CONAN_REMOTE_USER or CONAN_REMOTE_PASSWORD environment variables")
        sys.exit(1)

    # Login securely via stdin to avoid password in process listings
    run_command(
        ["conan", "remote", "login", "remote-package-repo", user],
        "📡 Sign into Conan Package Repository",
        input_data=password
    )

    run_command(
        ["conan", "upload", f"{args.library}/{args.version}",
            "--confirm", "-r=remote-package-repo"],
        f"🆙 Upload package version '{args.version}' to conan repo"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Build and upload Conan packages for libhal"
    )
    parser.add_argument("--library", required=True, help="Library name")
    parser.add_argument("--version", default="latest", help="Package version")
    parser.add_argument("--compiler_profile", required=True,
                        help="Conan compiler profile (arm-gcc or llvm)")
    parser.add_argument("--os", required=True, help="Target OS")
    parser.add_argument("--arch", required=True, help="Target architecture")
    parser.add_argument("--remote-urls", default="",
                        help="Comma-separated list of remote URLs")
    parser.add_argument("--build-types", default="Debug,MinSizeRel,Release",
                        help="Comma-separated list of build types")
    parser.add_argument("--settings-yml-url", default="",
                        help="URL for settings_user.yml")
    parser.add_argument("--settings-yml-path", default=".",
                        help="Path for settings_user.yml")
    parser.add_argument("--dir", default=".",
                        help="Directory where conan package exists")

    args = parser.parse_args()

    # Setup
    add_remotes(args.remote_urls)
    install_settings_yml(args.settings_yml_url, args.settings_yml_path)

    # Create packages for each build type
    build_types = [bt.strip()
                   for bt in args.build_types.split(",") if bt.strip()]
    for build_type in build_types:
        create_package(args, build_type)

    # Upload if not latest
    upload_packages(args)

    print("✅ Package and upload complete")


if __name__ == "__main__":
    main()
