#!/bin/bash

# # Use defaults
# ./baremetal_package.sh
#
# # Specify custom values
# ./baremetal_package.sh --dir ./myproject --version 1.2.3 --compiler-profile hal/tc/gcc --arch-list cortex-m0,cortex-m3,cortex-m4
#
# # Just change architecture list
# ./baremetal_package.sh --arch-list cortex-m0,cortex-m1,cortex-m3

# Exit script on any error
set -e

# Default values
DIR="."
VERSION="latest"
COMPILER_PROFILE="hal/tc/llvm"
ARCH_LIST=("cortex-m3")
CONAN_VERSION=2.23.0
EXTRA_CONAN_ARGS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dir)
      DIR="$2"
      shift 2
      ;;
    --version)
      VERSION="$2"
      shift 2
      ;;
    --compiler-profile)
      COMPILER_PROFILE="$2"
      shift 2
      ;;
    --conan-version)
      CONAN_VERSION="$2"
      shift 2
      ;;
    --arch-list)
      IFS=',' read -ra ARCH_LIST <<< "$2"
      shift 2
      ;;
    --extra-conan-args)
      EXTRA_CONAN_ARGS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--dir DIR] [--version VERSION] [--compiler-profile PROFILE] [--conan-version VERSION] [--arch-list ARCH1,ARCH2,...] [--extra-conan-args ARGS]"
      exit 1
      ;;
  esac
done

# Setup conan & libhal
pipx install conan>=$CONAN_VERSION
conan config install https://github.com/libhal/conan-config2.git
conan hal setup

# Loop over architectures and build types
for ARCH in "${ARCH_LIST[@]}"; do
  echo "Building for architecture: $ARCH"

  conan create $DIR -s:h build_type=Debug -s:h os=baremetal -s:h arch=$ARCH --version $VERSION -pr:h $COMPILER_PROFILE --build=missing $EXTRA_CONAN_ARGS

  conan create $DIR -s:h build_type=MinSizeRel -s:h os=baremetal -s:h arch=$ARCH --version $VERSION -pr:h $COMPILER_PROFILE --build=missing $EXTRA_CONAN_ARGS

  conan create $DIR -s:h build_type=Release -s:h os=baremetal -s:h arch=$ARCH --version $VERSION -pr:h $COMPILER_PROFILE --build=missing $EXTRA_CONAN_ARGS
done
