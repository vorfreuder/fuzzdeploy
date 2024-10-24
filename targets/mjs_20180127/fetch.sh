#!/bin/bash
# Date: 2018/01/27
# Version: 9eae0e6 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/cesanta/mjs "$TARGET/repo"
git -C "$TARGET/repo" checkout 9eae0e6 # 2018/01/27 htfuzz version
