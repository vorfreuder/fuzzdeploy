#!/bin/bash
# Date: 2021/07/21
# Version: v1.6.0-639

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/axiomatic-systems/Bento4 "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.6.0-639 # 2021/07/21
