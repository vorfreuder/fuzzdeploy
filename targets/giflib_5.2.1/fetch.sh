#!/bin/bash
# Date: 2019/06/24
# Version: 5.2.1 latest version
# https://giflib.sourceforge.net/

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://git.code.sf.net/p/giflib/code "$TARGET/repo"
git -C "$TARGET/repo" checkout 5.2.1
