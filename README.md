# [`libhal/ci`](https://github.com/libhal/ci) - Continuous Integration

The `libhal/ci` repository provides a collection of GitHub Actions workflows
that are designed to automate the process of building, testing, and deploying
software libraries for various hardware platforms. These workflows are designed
to be used with the libhal library, but can be adapted for use with other
libraries as well.

## Workflows

The repository contains the following workflows:

1. `demo_builder.yml`: This workflow builds a demo profile for a specified
   library. It installs necessary dependencies, sets up Conan profiles, and
   builds the package and demos for the specified profile.

2. `deploy.yml`: This workflow builds packages for every device and architecture
   that libhal supports. It uses the `deploy_unit.yml` workflow for each device
   and architecture.

3. `deploy_unit.yml`: This workflow is used by the `deploy.yml` workflow to
   build packages for a specific device and architecture.

4. `docs.yml`: This workflow is used to generate documentation for the library.
   It uses Doxygen to generate the documentation and then uploads the generated
   documentation as an artifact.

5. `library.yml`: This workflow is used to build and test a library. It installs
   necessary dependencies, sets up Conan profiles, builds the library, runs
   tests, and optionally generates code coverage reports.

6. `lint.yml`: This workflow is used to lint the code in the repository. It uses
   clang-format to format the code and clang-tidy to check the code for issues.

7. `platform_deploy.yml`: This workflow is used to build packages for a specific
   platform. It installs necessary dependencies, sets up Conan profiles, and
   builds the package for the specified platform.

8. `publish.yml`: This workflow is used to publish the library. It generates a
   badge for the latest version of the library, sets up GitHub Pages, and
   deploys the documentation to GitHub Pages.

9. `self_check.yml`: This workflow is used to run a series of checks on the
   library. It uses the `library.yml` and `platform_deploy.yml` workflows to
   build and test the library on various platforms.

10. `take.yml`: This workflow is used to assign issues to contributors. When a
    contributor comments on an issue with the word "take", the workflow assigns
    the issue to the contributor.

11. `tests.yml`: This workflow is used to run tests on the library. It installs
    necessary dependencies, sets up Conan profiles, builds the library, runs
    tests, and optionally generates code coverage reports.

## Usage

To use these workflows in your own repository, you can reference them in your
own GitHub Actions workflows. For example, the `libhal/libhal-stm32f1`
repository uses these workflows in its `ci.yml` workflow.

Here is an example of how to use the `library.yml` and `platform_deploy.yml`
workflows from the `libhal/ci` repository:

```yaml
name: ✅ Checks

on:
  workflow_dispatch:
  pull_request:
  push:
    tags:
      - "*"
    branches:
      - main
  schedule:
    - cron: "0 12 * * 0"

jobs:
  # Unit test, lint, and doc generation
  ci:
    uses: libhal/ci/.github/workflows/library.yml@4.0.0
    secrets: inherit

  # Test profile stm32f103c8 & upload prebuilt binaries to repository
  cortex-m3:
    uses: libhal/ci/.github/workflows/platform_deploy.yml@4.0.0
    with:
      profile: stm32f103c8
      upload: true
      processor_profile: https://github.com/libhal/libhal-armcortex.git
    secrets: inherit

  # Build platform based on profile& build p
  stm32f103c4:
    uses: libhal/ci/.github/workflows/platform_deploy.yml@4.0.0
    with:
      profile: stm32f103c4
      processor_profile: https://github.com/libhal/libhal-armcortex.git
    secrets: inherit

  # Required for libhal libraries to generate releases when a new tag version
  # is pushed. Highly recommended for open source libhal libraries.
  release:
    needs: [ci, cortex-m3, stm32f103c4, stm32f103zd]
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-22.04
    steps:
      - name: Release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          generate_release_notes: true
```

In this example, the `libhal` job uses the `library.yml` workflow to build and
test the `libhal` library, and the `libhal-stm32f1` job uses the
`platform_deploy.yml` workflow to build packages for the `libhal-stm32f1`
library for the `stm32f1` platform.

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
    uses: libhal/ci/.github/workflows/library.yml@3.0.3
    with:
      library: libhal-esp8266
      coverage: true
    secrets: inherit
  deploy:
    uses: libhal/ci/.github/workflows/deploy.yml@3.0.3
    secrets: inherit
  build_lpc4078:
    uses: libhal/ci/.github/workflows/demo_builder.yml@3.0.3
    with:
      profile: lpc4078
      processor_profile: https://github.com/libhal/libhal-armcortex.git
      platform_profile: https://github.com/libhal/libhal-lpc40.git
    secrets: inherit
```

In this workflow:

- The `ci` job uses the `library.yml` workflow from `libhal/ci` to build and
  test the `libhal-esp8266` library. Code coverage is enabled for this job.

- The `deploy` job uses the `deploy.yml` workflow from `libhal/ci` to build
  packages for the `libhal-esp8266` library.

- The `build_lpc4078` job uses the `demo_builder.yml` workflow from `libhal/ci`
  to build a demo for the `libhal-esp8266` library for the `lpc4078` platform.
  The `processor_profile` and `platform_profile` inputs specify the profiles to
  use for the processor and platform, respectively.

To use the `libhal/ci` workflows with your own device-specific library, you can
follow the same pattern as the `libhal-esp8266` library. Just replace
`libhal-esp8266` with the name of your library, and adjust the
`processor_profile` and `platform_profile` inputs as needed for your device.

## Detailed Workflow Descriptions

### library.yml

The `library.yml` workflow is used to build and test a library. It installs
necessary dependencies, sets up Conan profiles, builds the library, runs tests,
and optionally generates code coverage reports.

Inputs:

- `library`: The name of the library to build and test. Default is the name of
  the repository where the workflow is running.
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
- `skip_deploy`: A boolean value indicating whether to skip the deployment step.
  Default is false.
- `app_folder`: The directory where the application code for the library is
  located. Default is "demos".
- `repo`: The GitHub repository where the library is located. Default is the
  repository where the workflow is running.
- `conan_version`: The version of Conan to use for building the library. Default
  is "2.0.14".

This workflow is designed to be used in any GitHub Actions workflow by
referencing it with the `uses` keyword and providing the necessary inputs. If an
input is not provided, the workflow will use the default value.

### deploy.yml

The `deploy.yml` workflow is used to build packages for every device and
architecture that libhal supports. It uses the `deploy_unit.yml` workflow for
each device and architecture.

Inputs:

- `library`: The name of the library to build packages for. Default is the name
  of the repository where the workflow is running.
- `repo`: The GitHub repository where the library is located. Default is the
  repository where the workflow is running.
- `conan_version`: The version of Conan to use for building the library. Default
  is "2.0.14".

This workflow creates a job for each supported device and architecture. Each job
uses the `deploy_unit.yml` workflow to build a package for the specified device
and architecture. The `profile` and `profile_source` inputs for the
`deploy_unit.yml` workflow are set to the name of the device and the URL of the
profile for the device, respectively.

This workflow is designed to be used in any GitHub Actions workflow by
referencing it with the `uses` keyword and providing the necessary inputs. If an
input is not provided, the workflow will use the default value.

### platform_deploy.yml

The `platform_deploy.yml` workflow is used to build packages for a specific
platform. It installs necessary dependencies, sets up Conan profiles, and builds
the package for the specified platform.

Inputs:

- `library`: The name of the library to build packages for. Default is the name
  of the repository where the workflow is running.
- `repo`: The GitHub repository where the library is located. Default is the
  repository where the workflow is running.
- `conan_version`: The version of Conan to use for building the library. Default
  is "2.0.14".
- `profile`: The profile to use for building the package. This input is
  required.
- `upload`: A boolean value indicating whether to upload the built package to
  the `libhal` Conan repository. Default is false.
- `processor_profile`: The URL of the processor profile to use for building the
  package. Default is an empty string.

This workflow runs on an Ubuntu 22.04 runner. It checks out the code for the
library, installs Conan, adds the `libhal` Conan repository to the
Conan remotes, creates and sets up the default Conan profile, signs into JFrog
Artifactory if the workflow is running on the `main` branch, installs the libhal
settings_user.yml file, installs host OS profiles, installs processor profiles
if a `processor_profile` input is provided, installs platform profiles, and
creates packages for the `Debug`, `RelWithDebInfo`, `MinSizeRel`, and `Release`
build types for the specified profile. It also builds demos for the specified
profile. If the `upload` input is true and the workflow is running on a tag, it
uploads the built package to the `libhal` Conan repository.

This workflow is designed to be used in any GitHub Actions workflow by
referencing it with the `uses` keyword and providing the necessary inputs. If an
input is not provided, the workflow will use the default value.

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
  is "2.0.14".
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

## Disclaimer

This project is not an official Google project. It is not supported by Google
and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.
