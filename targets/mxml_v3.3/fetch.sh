#!/bin/bash
# Date: 2021/11/06
# Version: v3.3

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/michaelrsweet/mxml "$TARGET/repo"
git -C "$TARGET/repo" checkout v3.3
