#!/bin/bash
# Date: 2022/02/22
# Version: v1.0.1

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/gpac/gpac "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.0.0
