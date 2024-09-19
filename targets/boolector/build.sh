#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
# Download and build Lingeling
CC=clang CXX=clang++ CFLAGS= CXXFLAGS= ./contrib/setup-lingeling.sh -O0 -g -asan
# Download and build BTOR2Tools
CC=clang CXX=clang++ CFLAGS= CXXFLAGS= ./contrib/setup-btor2tools.sh -O0 -g -asan
# Build Boolector
unset AFL_USE_ASAN
./configure.sh -g --asan
cd build
make -j $(nproc)

cp bin/boolector "$PROGRAM"
