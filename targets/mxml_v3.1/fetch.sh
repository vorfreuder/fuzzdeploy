#!/bin/bash
# Date: 2019/08/28
# Version: v3.1

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/michaelrsweet/mxml "$TARGET/repo"
git -C "$TARGET/repo" checkout v3.1
