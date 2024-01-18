#!/bin/bash
# Date: 2017/03/07
# Version: 6caf151 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/yasm/yasm "$TARGET/repo"
git -C "$TARGET/repo" checkout 6caf151 # 2017/03/07 htfuzz version
