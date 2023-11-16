#!/bin/bash
# Date: 2014/12/22
# Version: 72e31ff uafuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://git.code.sf.net/p/giflib/code "$TARGET/repo"
git -C "$TARGET/repo" checkout 72e31ff # 2014/12/22 uafuzz version
