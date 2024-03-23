#!/bin/bash
# Date: 2019/04/02
# Version: v2.3.1

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/uclouvain/openjpeg.git "$TARGET/repo"
# git -C "$TARGET/repo" checkout v2.5.0 # 2022/05/14
# git -C "$TARGET/repo" checkout 6af3931 # 2023/09/23
git -C "$TARGET/repo" checkout v2.3.1 # 2019/04/02
