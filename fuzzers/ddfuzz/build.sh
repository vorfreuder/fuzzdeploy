#!/bin/bash
set -e

if [ ! -d "$FUZZER/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$FUZZER/repo"
export CC=clang
export CXX=clang++
sed -i.bak 's/^	-/	/g' GNUmakefile
make clean
make source-only NO_NYX=1
mv GNUmakefile.bak GNUmakefile
