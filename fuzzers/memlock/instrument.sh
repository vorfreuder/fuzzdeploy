#!/bin/bash
set -e

export CC="$FUZZER/repo/memlock-heap-clang"
export CXX="$FUZZER/repo/memlock-heap-clang++"
export AFL_USE_ASAN=1
bash "$TARGET/build.sh"
