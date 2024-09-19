#!/bin/bash
# Date: 2020/11/26
# Version: 7804849 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/gpac/gpac "$TARGET/repo"
git -C "$TARGET/repo" checkout 7804849 # 2020/11/26 htfuzz version
