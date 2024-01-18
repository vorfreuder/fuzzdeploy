#!/bin/bash
# Date: 2016/11/05
# Version: version-1.900.20 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/jasper-software/jasper "$TARGET/repo"
git -C "$TARGET/repo" checkout version-1.900.20 # 2016/11/05 htfuzz version
