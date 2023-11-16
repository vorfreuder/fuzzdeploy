#!/bin/bash
# Date: 2023/09/21
# Version: 9defefa latest commit

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/yasm/yasm "$TARGET/repo"
git -C "$TARGET/repo" checkout 9defefa
