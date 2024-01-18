#!/bin/bash
set -e

export CC="$FUZZER/repo/afl-clang-fast"
export CXX="$FUZZER/repo/afl-clang-fast++"
export AS="/usr/bin/llvm-as"
export AR="/usr/bin/llvm-ar"
export RANLIB="/usr/bin/llvm-ranlib"
export AFL_USE_ASAN=1
export AFL_LLVM_INSTRUMENT=CLASSIC
bash "$TARGET/build.sh"
