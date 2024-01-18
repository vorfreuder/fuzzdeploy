#!/bin/bash
# Date: 2023/11/04
# Version: version-4.1.0 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/jasper-software/jasper "$TARGET/repo"
git -C "$TARGET/repo" checkout version-4.1.0 # 2023/11/04
