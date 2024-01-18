#!/bin/bash
# Date: 2022/7/25
# Version: v3.3.1 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/michaelrsweet/mxml "$TARGET/repo"
git -C "$TARGET/repo" checkout v3.3.1 # 2022/7/25
