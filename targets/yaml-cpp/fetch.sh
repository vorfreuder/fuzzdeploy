#!/bin/bash
# Date: 2023/08/11
# Version: 0.8.0 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/jbeder/yaml-cpp "$TARGET/repo"
git -C "$TARGET/repo" checkout 0.8.0 # 2023/08/11
