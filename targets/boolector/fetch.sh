#!/bin/bash
# Date: 2023/09/12
# Version: 3.2.3 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/Boolector/boolector "$TARGET/repo"
git -C "$TARGET/repo" checkout 3.2.3 # 2023/09/12
