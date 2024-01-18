#!/bin/bash
# Date: 2019/12/19
# Version: 4c19ae5 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/gpac/gpac "$TARGET/repo"
git -C "$TARGET/repo" checkout 4c19ae5 # 2019/12/19 htfuzz version
