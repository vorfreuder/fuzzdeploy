#!/bin/bash
set -e

export CC="/usr/bin/clang"
export CXX="/usr/bin/clang++"
export CFLAGS="-fsanitize=address -fno-omit-frame-pointer -g"
export CXXFLAGS="-fsanitize=address -fno-omit-frame-pointer -g"
export LDFLAGS="-fsanitize=address -fno-omit-frame-pointer -g"
export AS="/usr/bin/llvm-as"
export AR="/usr/bin/llvm-ar"
export RANLIB="/usr/bin/llvm-ranlib"
bash "$TARGET/build.sh"
