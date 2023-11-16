#!/bin/bash
# Date: 2023/08/09
# Version: v2.11.5 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/GNOME/libxml2 "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.11.5 # 2023/08/09
