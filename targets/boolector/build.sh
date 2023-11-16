#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
# Download and build Lingeling
CC=clang CXX=clang++ ./contrib/setup-lingeling.sh
# Download and build BTOR2Tools
CC=clang CXX=clang++ ./contrib/setup-btor2tools.sh
# Build Boolector
unset AFL_USE_ASAN
./configure.sh -g --asan
cd build
make -j $(nproc)

cp bin/boolector "$OUT"
