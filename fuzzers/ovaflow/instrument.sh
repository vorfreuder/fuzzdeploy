#!/bin/bash
set -e

export CC="$FUZZER/repo/afl-clang-fast"
export CXX="$FUZZER/repo/afl-clang-fast++"
export AFL_USE_ASAN=1
bash "$TARGET/build.sh"
