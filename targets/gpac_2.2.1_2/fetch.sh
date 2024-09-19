#!/bin/bash
# Date: 2023/04/27
# Version: v2.2.1 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/gpac/gpac "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.2.1 # 2023/04/27
