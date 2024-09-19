#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
export ASAN_OPTIONS=detect_leaks=0 # Centos7 needs
./configure
make -j $(nproc)

cp src/cflow "$PROGRAM"
