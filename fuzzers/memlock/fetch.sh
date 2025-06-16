#!/bin/bash
set -e

if [ -d "$FUZZER/repo" ]; then
    exit 0
fi

git clone --depth 1 https://github.com/wcventure/MemLock-Fuzz "$FUZZER/repo"
mv "$FUZZER/repo/tool/MemLock"/* "$FUZZER/repo"
