#!/bin/bash
# Date: 2023/08/10
# Version: v1.5.5 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/tjko/jpegoptim "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.5.5 # 2023/08/10
