#!/bin/bash
# Date: 2019/10/30
# Version: v2.9.10

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/GNOME/libxml2 "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.9.10
