#!/bin/bash
# Date: 2022/03/09
# Version: v0.651 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/ckolivas/lrzip "$TARGET/repo"
git -C "$TARGET/repo" checkout v0.651 # 2022/03/09
