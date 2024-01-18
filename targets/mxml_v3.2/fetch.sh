#!/bin/bash
# Date: 2020/10/09
# Version: v3.2

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/michaelrsweet/mxml "$TARGET/repo"
git -C "$TARGET/repo" checkout v3.2
