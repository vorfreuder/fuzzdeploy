#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
export ASAN_OPTIONS=detect_leaks=0
./configure --disable-shared
make -j $(nproc)

cp binutils/objdump "$PROGRAM"
