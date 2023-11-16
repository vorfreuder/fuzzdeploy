#!/bin/bash
set -e

if [ -d "$FUZZER/repo" ]; then
    exit 0
fi

git clone --depth 1 https://github.com/zhanggenex/ovAFLow "$FUZZER/repo"
mv "$FUZZER/repo/mem_func"/* "$FUZZER/repo"
