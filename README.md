# [`libhal/ci`](https://github.com/libhal/ci) - Continuous Integration

The `libhal/ci` repository provides a collection of GitHub Actions workflows
that are designed to automate the process of building, testing, and deploying
software libraries for various hardware platforms. These workflows are designed
to be used with the libhal library, but can be adapted for use with other
libraries as well.

## Workflows

The repository contains the following workflows:

1. `demo_builder.yml`: Builds a demo profile for a specified
   library. It installs necessary dependencies, sets up Conan profiles, and
   builds the package and demos for the specified profile.

2. `deploy_all.yml`: Builds packages for every device and
   architecture that libhal supports. It uses the `deploy.yml` workflow for each device and architecture.

3. `deploy.yml`: Used by the `deploy_all.yml` workflow to build packages for a
   specific device and architecture.

4. `deploy_linux.yml`: A workflow used by `deploy_all.yml` to deploy
   specifically to linux using the `conan-config/linux/` profile.

5. `docs.yml`: Used to generate documentation for the library. It uses Doxygen
   to generate the documentation and then uploads the generated documentation
   as an artifact.

6. `library_check.yml`: Used to build and test a library. It installs
   necessary dependencies, sets up Conan profiles, builds the library, runs
   tests, and optionally generates code coverage reports.

7. `lint.yml`: Used to lint the code in the repository. It uses
   clang-format to format the code and clang-tidy to check the code for issues.

8. `platform_deploy.yml`: Used to build packages for a specific
   platform. It installs necessary dependencies, sets up Conan profiles, and
   builds the package for the specified platform.

9. `self_check.yml`: Used to run a series of checks on various libraries to
   determine if all of the workflows still work as intended.

10. `take.yml`: Used to assign issues to contributors. When a
    contributor comments on an issue with the word "take", the workflow assigns
    the issue to the contributor.

11. `tests.yml`: Used to run tests on the library. It installs
    necessary dependencies, sets up Conan profiles, builds the library, runs
    tests, and optionally generates code coverage reports.

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
      platform_profile_url: https://github.com/libhal/libhal-lpc40.git
      platform_profile: v2/lpc4078
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

### library_check.yml

The `library_check.yml` workflow is used to build and test a library. It
installs necessary dependencies, sets up Conan profiles, builds the library, runs tests, and optionally generates code coverage reports.

Inputs:

- `library`: The name of the library to build and test. Default is the name of
  the repository where the workflow is running.
- `version`: library version number which should correspond to a tag number in
  the repo. Do not supply this field if you want to perform a dry-run and not deploy to the server.
- `coverage`: A boolean value indicating whether to generate code coverage
  reports. Default is true.
- `fail_on_coverage`: A boolean value indicating whether the workflow should
  fail if the code coverage does not meet the specified threshold. Default is
  false.
- `coverage_threshold`: A string specifying the minimum and maximum code
  coverage thresholds. The workflow will generate a warning if the code coverage
  is below the minimum threshold and an error if it is above the maximum
  threshold. Default is "40 80".
- `source_dir`: The directory where the source code for the library is located.
  Default is "include/".
- `repo`: The GitHub repository where the library is located. Default is the
  repository where the workflow is running.
- `conan_version`: The version of Conan to use for building the library. Default
  is "2.2.2".

This workflow is designed to be used in any GitHub Actions workflow by
referencing it with the `uses` keyword and providing the necessary inputs. If an
input is not provided, the workflow will use the default value.

### deploy_all.yml

This profile is the correct profile to be used for device libraries, or
libraries that are agnostic to the CPU it is running on.

The `deploy.yml` workflow is used to build packages for every device and
architecture that libhal supports. It uses the `deploy.yml` and
`deploy_linux.yml` workflow for each device and architecture.

Inputs:

- `library`: The name of the library to build packages for. Default is the name
  of the repository where the workflow is running.
- `version`: library version number which should correspond to a tag number in
  the repo. Do not supply this field if you want to perform a dry-run and not deploy to the server.
- `repo`: The GitHub repository where the library is located. Default is the
  repository where the workflow is running.
- `conan_version`: The version of Conan to use for building the library. Default
  is "2.2.2".

This workflow creates a job for each supported device and architecture. Each job
uses the `deploy.yml` workflow to build a package for the specified device
and architecture.

This workflow is designed to be used in any GitHub Actions workflow by
referencing it with the `uses` keyword and providing the necessary inputs. If an
input is not provided, the workflow will use the default value.

### deploy.yml

> [!NOTE]
> Docs not written yet.

### demo_builder.yml

The `demo_builder.yml` workflow builds a demo profile for a specified library.
It installs necessary dependencies, sets up Conan profiles, and builds the
package and demos for the specified profile.

Inputs:

- `library`: The name of the library to build a demo for. Default is the name of
  the repository where the workflow is running.
- `repo`: The GitHub repository where the library is located. Default is the
  repository where the workflow is running.
- `conan_version`: The version of Conan to use for building the library. Default
  is "2.2.2".
- `profile`: The profile to use for building the demo. This input is required.
- `processor_profile`: The URL of the processor profile to use for building the
  demo. Default is an empty string.
- `platform_profile`: The URL of the platform profile to use for building the
  demo. Default is an empty string.

This workflow runs on an Ubuntu 22.04 runner. It checks out the code for the
library, installs Conan, adds the `libhal` Conan repository to the
Conan remotes, creates and sets up the default Conan profile, signs into JFrog
Artifactory if the workflow is running on the `main` branch, installs the libhal
settings_user.yml file, installs host OS profiles, installs processor profiles
if a `processor_profile` input is provided, installs platform profiles if a
`platform_profile` input is provided, builds a package for the specified profile
with the `MinSizeRel` build type, and builds demos for the specified profile
with the `MinSizeRel` build type.

This workflow is designed to be used in any GitHub Actions workflow by
referencing it with the `uses` keyword and providing the necessary inputs. If an
input is not provided, the workflow will use the default value.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.
