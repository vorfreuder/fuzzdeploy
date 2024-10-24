#!/bin/bash
# Date: 2017/08/14
# Version: fad477c uafuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/kohler/gifsicle "$TARGET/repo"
git -C "$TARGET/repo" checkout fad477c # 2017/08/14 uafuzz version
