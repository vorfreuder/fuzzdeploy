#!/bin/bash
set -e

export CC="$FUZZER/repo/bb_metric/afl-clang-fast"
export CXX="$FUZZER/repo/bb_metric/afl-clang-fast++"
export AFL_USE_ASAN=1
bash "$TARGET/build.sh"
