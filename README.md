# [`libhal/ci`](https://github.com/libhal/ci) - Continuous Integration

The `libhal/ci` repository provides a collection of GitHub Actions workflows
that are designed to automate the process of building, testing, and deploying
software libraries for various hardware platforms. These workflows are designed
to be used with the libhal library, but can be adapted for use with other
libraries as well.

## Executing Workflows Locally

To test work flows locally on your machine, use the
[`act`](https://nektosact.com/introduction.html) command.

## Workflows

The repository contains the following callable workflows:

### Current Workflows

1. `api_docs_gen.yml`: Generates API documentation using Doxygen and deploys it
   to the API documentation repository. This workflow is triggered on releases.

2. `app_builder2.yml`: Builds applications for a specified platform. Replaces
   the deprecated `app_builder.yml` and `demo_builder.yml` workflows with a
   unified approach using conan-config2.

3. `docs.yml`: Validates public API documentation using Doxygen. Checks that
   all public APIs are properly documented and generates warnings for missing
   documentation.

4. `library_check.yml`: Runs a complete suite of checks on a library including
   tests, linting, and documentation validation. This is the primary CI
   workflow for library development.

5. `lint.yml`: Checks code formatting using clang-format. Validates that code
   follows the libhal style guide for `include/`, `src/`, `demos/`, and
   `tests/` directories.

6. `package_and_upload.yml`: Creates Conan packages for a specific platform and
   optionally uploads them to a Conan repository. Replaces the deprecated
   `deploy.yml`, `deploy_linux.yml`, and `deploy_mac.yml` workflows.

7. `package_and_upload_all.yml`: Creates Conan packages for all supported
   platforms and architectures that libhal supports. Replaces the deprecated
   `deploy_all.yml` workflow.

8. `tests.yml`: Runs unit tests for a library on multiple platforms (Linux,
   macOS, and optionally Windows) with optional code coverage reporting.

### Internal Workflows

These workflows are used internally by the libhal/ci repository and are not
typically called directly by other repositories:

- `rebase.yml`: Automatically rebases the 5.x.y branch onto main
- `self_check.yml`: Runs checks on various libhal libraries to ensure workflows
  are functioning correctly
- `take.yml`: Allows contributors to self-assign issues by commenting `.take`

## Usage

To use these workflows in your own repository, you can reference them in your
own GitHub Actions workflows. For example, the `libhal/libhal-stm32f1`
repository uses these workflows in its `ci.yml` workflow.

Here is an example of how to use the `library_check.yml`, `demo_builder.yml`, and `deploy.yml` workflows from the `libhal/ci` repository:

```yaml

name: ✅ CI

on:
  workflow_dispatch:
  pull_request:
  push:
    branches:
      - main
  # Every week re-run these checks to see if changes to the ecosystem have
  # broken this package.
  schedule:
    - cron: "0 12 * * 0"

jobs:
  # Build and run unit tests on the library package
  library_checks:
    uses: libhal/ci/.github/workflows/library_check.yml@5.x.y
    secrets: inherit

  # Check the deploy flow. Without the "version" parameter specified, deploy
  # runs a dry run of the deploy without pushing anything to the server.
  deploy_cortex-m4f_check:
    uses: libhal/ci/.github/workflows/deploy.yml@5.x.y
    with:
      arch: cortex-m4f
      os: baremetal
      compiler: gcc
      compiler_version: 12.3
      compiler_package: arm-gnu-toolchain
    secrets: inherit

  # Build the demo for a specific chip. Because most of the stm32f1
  # architectures are "mostly" the same besides their flash and ram size, if
  # demos build one for chip then it should work for others.
  demo_check:
    uses: libhal/ci/.github/workflows/demo_builder.yml@5.x.y
    with:
      compiler_profile_url: https://github.com/libhal/arm-gnu-toolchain.git
      compiler_profile: v1/arm-gcc-12.3
      platform_profile_url: https://github.com/libhal/libhal-stm32f1.git
      platform_profile: v2/stm32f103c8
    secrets: inherit
```

## Device Libraries

The `libhal/ci` workflows can also be used with device-specific libraries. These
libraries provide implementations of the libhal interfaces for specific devices.

### Example: libhal-esp8266

The `libhal-esp8266` library provides an implementation of the libhal interfaces
for the ESP8266 device. The library uses the `libhal/ci` workflows to automate
building, testing, and deploying the library.

The `ci.yml` workflow for the `libhal-esp8266` library is as follows:

```yaml
name: ✅ CI

on:
  workflow_dispatch:
  pull_request:
  push:
    branches:
      - main
  schedule:
    - cron: "0 12 * * 0"

jobs:
  ci:
    uses: libhal/ci/.github/workflows/library_check.yml@5.x.y
    secrets: inherit

  deploy_cortex-m4f_check:
    uses: libhal/ci/.github/workflows/deploy.yml@5.x.y
    with:
      arch: cortex-m4f
      os: baremetal
      compiler: gcc
      compiler_version: 12.3
      compiler_package: arm-gnu-toolchain
    secrets: inherit

  demo_check:
    uses: libhal/ci/.github/workflows/demo_builder.yml@5.x.y
    with:
      compiler_profile_url: https://github.com/libhal/arm-gnu-toolchain.git
      compiler_profile: v1/arm-gcc-12.3
      platform_profile_url: https://github.com/libhal/libhal-arm-mcu.git
      platform_profile: v1/lpc4078
    secrets: inherit

```

In this workflow:

- The `ci` job uses the `library_check.yml` workflow from `libhal/ci` to build
  and test the `libhal-esp8266` library. Code coverage is enabled for this job.

- The `deploy` job uses the `deploy.yml` workflow from `libhal/ci` to build
  packages for the `libhal-esp8266` library for the `cortex-m4f` processor.
  This simply shows that the package can be built for this specific
  architecture. Because the library doesn't have anything that wouldn't work
  between different cortex-m CPU, only deploying for one architecture should be
  enough.

- The `demo_check` job uses the `demo_builder.yml` workflow from `libhal/ci`
  to build a demo for the `libhal-esp8266` library for the `lpc4078` platform.
  The `processor_profile` and `platform_profile` inputs specify the profiles to
  use for the processor and platform, respectively.

To use the `libhal/ci` workflows with your own device-specific library, you can
follow the same pattern as the `libhal-esp8266` library. Just replace
`libhal-esp8266` with the name of your library, and adjust the
`processor_profile` and `platform_profile` inputs as needed for your device.

> [!IMPORTANT]
> This section is missing the new way we run deployments. Specifically using the
> deploy_all.yml along with a tag number.

## Detailed Workflow Descriptions

### api_docs_gen.yml

Generates and deploys API documentation for libhal libraries.

**Inputs:**

- None (uses repository name and version from GitHub context)

**Usage:**

```yaml
jobs:
  api_docs:
    uses: libhal/ci/.github/workflows/api_docs_gen.yml@5.x.y
    secrets: inherit
```

### app_builder2.yml

Builds applications/demos for embedded platforms using the new conan-config2 system.

**Inputs:**

- `repo` (string): GitHub repository to build from. Default: current repository
- `version` (string): Version/tag to checkout. Default: "" (uses current branch)
- `conan_version` (string): Conan version to use. Default: "2.16.1"
- `compiler_profile` (string, **required**): Compiler profile path (e.g., "hal/tc/arm-gcc-12.3")
- `platform_profile` (string, **required**): Platform profile path (e.g., "hal/mcu/lpc4078")
- `config2_version` (string): Branch/tag of conan-config2 to use. Default: "main"
- `dir` (string): Directory containing the application. Default: "."
- `library_dir` (string): Directory containing the directory of a library
  needed for the application to build. The library's version will be hard set
  to `latest`. If this input is left empty, then the library build step is
  skipped. Default: "".

**Usage:**

```yaml
jobs:
  build_demo:
    uses: libhal/ci/.github/workflows/app_builder2.yml@5.x.y
    with:
      compiler_profile: hal/tc/arm-gcc-12.3
      platform_profile: hal/mcu/lpc4078
    secrets: inherit
```

### docs.yml

Validates that all public APIs are properly documented using Doxygen.

**Inputs:**

- `library` (string, **required**): Name of the library
- `source_dir` (string, **required**): Source directory to document
- `repo` (string, **required**): GitHub repository location
- `version` (string): Version/tag to checkout. Default: "" (uses current branch)
- `dir` (string, **required**): Directory containing the Conan package

**Usage:**

```yaml
jobs:
  docs:
    uses: libhal/ci/.github/workflows/docs.yml@5.x.y
    with:
      library: libhal-actuator
      source_dir: src
      repo: libhal/libhal-actuator
      dir: .
    secrets: inherit
```

### library_check.yml

Comprehensive CI workflow that runs tests, linting, and documentation checks.

**Inputs:**

- `library` (string): Library name. Default: repository name
- `version` (string): Version/tag to checkout. Default: "" (dry-run, no deployment)
- `coverage` (boolean): Enable code coverage reporting. Default: true
- `fail_on_coverage` (boolean): Fail if coverage threshold not met. Default: false
- `coverage_threshold` (string): Min/max coverage thresholds. Default: "40 80"
- `source_dir` (string): Source code directory. Default: "src"
- `repo` (string): GitHub repository. Default: current repository
- `conan_version` (string): Conan version. Default: "2.22.2"
- `dir` (string): Conan package directory. Default: "."

**Usage:**

```yaml
jobs:
  ci:
    uses: libhal/ci/.github/workflows/library_check.yml@5.x.y
    with:
      coverage: true
      fail_on_coverage: false
      coverage_threshold: "40 80"
    secrets: inherit
```

### lint.yml

Validates code formatting using clang-format.

**Inputs:**

- `library` (string, **required**): Library name
- `source_dir` (string, **required**): Source directory to lint
- `repo` (string, **required**): GitHub repository
- `version` (string): Version/tag to checkout. Default: ""
- `dir` (string): Package directory. Default: "."

**Usage:**

```yaml
jobs:
  lint:
    uses: libhal/ci/.github/workflows/lint.yml@5.x.y
    with:
      library: libhal-util
      source_dir: src
      repo: libhal/libhal-util
    secrets: inherit
```

### package_and_upload.yml

Creates Conan packages for a specific platform/architecture and uploads to a repository.

**Inputs:**

- `library` (string): Library name. Default: repository name
- `repo` (string): GitHub repository. Default: current repository
- `conan_version` (string): Conan version. Default: "2.18.0"
- `config2_version` (string): conan-config2 branch/tag. Default: "main"
- `version` (string): Package version. Default: "latest" (no upload)
- `runner_os` (string, **required**): GitHub runner OS (e.g., "ubuntu-24.04", "macos-latest")
- `arch` (string, **required**): Target architecture (e.g., "x86_64", "cortex-m4f")
- `os` (string, **required**): Target OS (e.g., "Linux", "baremetal")
- `compiler_profile` (string, **required**): Compiler profile path
- `dir` (string): Conan package directory. Default: "."
- `remote_url` (string): Conan repository URL. Default: ""

**Secrets:**

- `conan_remote_user`: Username for Conan repository
- `conan_remote_password`: Password for Conan repository

**Usage:**
```yaml
jobs:
  deploy:
    uses: libhal/ci/.github/workflows/package_and_upload.yml@5.x.y
    with:
      runner_os: ubuntu-24.04
      arch: cortex-m4f
      os: baremetal
      compiler_profile: hal/tc/arm-gcc
      version: "1.0.0"
      remote_url: https://example.jfrog.io/artifactory/api/conan/my-repo
    secrets:
      conan_remote_user: ${{ secrets.CONAN_USER }}
      conan_remote_password: ${{ secrets.CONAN_PASSWORD }}
```

### package_and_upload_all.yml

Creates Conan packages for all supported platforms and architectures.

**Inputs:**

- `library` (string): Library name. Default: repository name
- `repo` (string): GitHub repository. Default: current repository
- `version` (string): Package version. Default: "latest" (no upload)
- `conan_version` (string): Conan version. Default: "2.22.2"
- `dir` (string): Conan package directory. Default: "."
- `remote_url` (string): Conan repository URL. Default: ""

**Secrets:**

- `conan_remote_user`: Username for Conan repository
- `conan_remote_password`: Password for Conan repository

Builds packages for:

- Linux x86_64 (LLVM)
- Linux armv8 (LLVM)
- macOS armv8 (LLVM)
- Cortex-M0+, M1, M3, M4, M4F, M7F, M7D (ARM GCC)
- Cortex-M23, M33, M33F, M35PF, M55, M85 (ARM GCC)

**Usage:**

```yaml
jobs:
  deploy_all:
    uses: libhal/ci/.github/workflows/package_and_upload_all.yml@5.x.y
    with:
      version: "1.0.0"
      remote_url: https://example.jfrog.io/artifactory/api/conan/my-repo
    secrets:
      conan_remote_user: ${{ secrets.CONAN_USER }}
      conan_remote_password: ${{ secrets.CONAN_PASSWORD }}
```

### tests.yml

Runs unit tests on multiple platforms with optional coverage reporting.

**Inputs:**

- `library` (string, **required**): Library name
- `version` (string): Version/tag to checkout. Default: ""
- `coverage` (boolean, **required**): Enable code coverage
- `fail_on_coverage` (boolean, **required**): Fail on coverage threshold
- `coverage_threshold` (string, **required**): Coverage thresholds
- `repo` (string, **required**): GitHub repository
- `conan_version` (string, **required**): Conan version
- `config2_version` (string): conan-config2 branch/tag. Default: "main"
- `dir` (string): Package directory. Default: "."
- `llvm` (string): **(DEPRECATED NO LONGER USED)**. Tests will use the latest
  version of LLVM available in the libhal conan-config2 repo.

Runs tests on:

- Ubuntu 24.04 (x86_64, Linux)
- macOS latest (armv8, macOS)

**Usage:**

```yaml
jobs:
  tests:
    uses: libhal/ci/.github/workflows/tests.yml@5.x.y
    with:
      library: libhal-util
      repo: libhal/libhal-util
      coverage: true
      fail_on_coverage: false
      coverage_threshold: "40 80"
      conan_version: "2.22.2"
    secrets: inherit
```

## Deprecated Workflows

The following workflows are deprecated and should not be used in new projects. They are maintained for backwards compatibility but will be removed in a future release.

### app_builder.yml (DEPRECATED)

**Status:** Deprecated - Use `app_builder2.yml` instead

This workflow has been replaced by `app_builder2.yml` which uses the new conan-config2 system for a more streamlined configuration approach.

### demo_builder.yml (DEPRECATED)

**Status:** Deprecated - Use `app_builder2.yml` instead

This workflow has been replaced by `app_builder2.yml`. The new workflow handles both applications and demos with a unified approach.

### deploy.yml (DEPRECATED)

**Status:** Deprecated - Use `package_and_upload.yml` instead

This workflow has been replaced by `package_and_upload.yml` which provides better configuration options and supports custom Conan repositories.

### deploy_all.yml (DEPRECATED)

**Status:** Deprecated - Use `package_and_upload_all.yml` instead

This workflow has been replaced by `package_and_upload_all.yml` which includes updated architecture support and uses the new conan-config2 system.

### deploy_linux.yml (DEPRECATED)

**Status:** Deprecated - Use `package_and_upload.yml` instead

This workflow has been replaced by `package_and_upload.yml` with `runner_os: ubuntu-24.04` specified.

### deploy_mac.yml (DEPRECATED)

**Status:** Deprecated - Use `package_and_upload.yml` instead

This workflow has been replaced by `package_and_upload.yml` with `runner_os: macos-latest` specified.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.
