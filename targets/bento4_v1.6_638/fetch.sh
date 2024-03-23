#!/bin/bash
# Date: 2021/06/12
# Version: v1.6.0-638

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/axiomatic-systems/Bento4 "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.6.0-638
