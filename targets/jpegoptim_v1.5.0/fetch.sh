#!/bin/bash
# Date: 2022/09/14
# Version: v1.5.0

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/tjko/jpegoptim "$TARGET/repo"
git -C "$TARGET/repo" checkout v1.5.0
