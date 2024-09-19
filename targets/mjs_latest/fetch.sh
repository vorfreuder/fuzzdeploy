#!/bin/bash
# Date: 2021/10/28
# Version: b1b6eac latest commit

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/cesanta/mjs "$TARGET/repo"
git -C "$TARGET/repo" checkout b1b6eac # 2021/10/28
