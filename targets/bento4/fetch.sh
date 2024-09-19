#!/bin/bash
# Date: 2023/05/20
# Version: v1.6.0-640 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/axiomatic-systems/Bento4 "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.6.0-640 # 2023/05/20
