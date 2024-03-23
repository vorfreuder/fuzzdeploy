#!/bin/bash
# Date: 2020/06/13
# Version: v1.6.0-637

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/axiomatic-systems/Bento4 "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.6.0-637
