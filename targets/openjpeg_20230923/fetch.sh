#!/bin/bash
# Date: 2023/09/23
# Version: 6af3931 latest commit

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/uclouvain/openjpeg.git "$TARGET/repo"
# git -C "$TARGET/repo" checkout v2.5.0 # 2022/05/14
git -C "$TARGET/repo" checkout 6af3931 # 2023/09/23
