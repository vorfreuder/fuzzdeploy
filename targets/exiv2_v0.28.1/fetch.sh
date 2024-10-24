#!/bin/bash
# Date: 2023/05/14
# Version: v0.28.1 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/Exiv2/exiv2 "$TARGET/repo"
# git -C "$TARGET/repo" checkout v0.27.7 # 2023/05/14
git -C "$TARGET/repo" checkout v0.28.1 # 2023/11/06
