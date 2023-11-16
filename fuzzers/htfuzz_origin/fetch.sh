#!/bin/bash
set -e

if [ -d "$FUZZER/repo" ]; then
    exit 0
fi

git clone --depth 1 https://github.com/sharedata21/HTFuzz "$FUZZER/repo"
mv "$FUZZER/repo/tool/tool/HTFuzz"/* "$FUZZER/repo"
