#!/bin/bash
set -e

export CC="/usr/bin/clang"
export CXX="/usr/bin/clang++"
export CFLAGS="$CFLAGS -fprofile-arcs -ftest-coverage -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION -g -O0 -ldl"
export CXXFLAGS="$CXXFLAGS $CFLAGS"
export LDFLAGS="$LDFLAGS --coverage"
export AS="/usr/bin/llvm-as"
export AR="/usr/bin/llvm-ar"
export RANLIB="/usr/bin/llvm-ranlib"
bash "$TARGET/build.sh"
