#!/bin/bash
# Date: 2019/02/11
# Version: 5.1.5
# https://giflib.sourceforge.net/

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://git.code.sf.net/p/giflib/code "$TARGET/repo"
# git -C "$TARGET/repo" checkout 72e31ff # 2014/12/22 uafuzz version. no proper corpus
git -C "$TARGET/repo" checkout 5.1.5
