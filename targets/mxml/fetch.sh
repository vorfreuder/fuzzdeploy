#!/bin/bash
# Date: 2018/08/02
# Version: v2.12 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/michaelrsweet/mxml "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.12 # 2018/08/02 htfuzz version
