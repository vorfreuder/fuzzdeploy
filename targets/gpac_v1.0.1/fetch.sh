#!/bin/bash
# Date: 2020/09/11
# Version: v1.0.1

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/gpac/gpac "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.0.1
