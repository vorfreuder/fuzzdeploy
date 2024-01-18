#!/bin/bash
# Date: 2017/04/26
# Version: v0.26

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/Exiv2/exiv2 "$TARGET/repo"
# git -C "$TARGET/repo" checkout v0.27.7 # 2023/05/14
git -C "$TARGET/repo" checkout v0.26
