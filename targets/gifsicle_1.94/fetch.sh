#!/bin/bash
# Date: 2023/06/23
# Version: v1.94 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/kohler/gifsicle "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.94
