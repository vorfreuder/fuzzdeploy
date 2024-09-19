#!/bin/bash
# Date: 2021/05/13
# Version: v2.9.11

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/GNOME/libxml2 "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.9.11 # 2021/05/13
