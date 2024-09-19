#!/bin/bash
# Date: 2022/04/12
# Version: v1.4.7

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/tjko/jpegoptim "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.4.7
