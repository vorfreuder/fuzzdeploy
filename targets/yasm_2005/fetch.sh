#!/bin/bash
# Date: 2020/05/04
# Version: c9db6d7

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/yasm/yasm "$TARGET/repo"
git -C "$TARGET/repo" checkout c9db6d70a9ab62ce58a1cf123f2007d7a3ccc528
