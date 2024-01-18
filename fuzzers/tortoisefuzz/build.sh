#!/bin/bash
set -e

if [ ! -d "$FUZZER/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$FUZZER/repo"
CC=clang make -j $(nproc)
