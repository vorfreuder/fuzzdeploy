#!/bin/bash
# Date: 2010/09/06
# Version: 962d606 uafuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone git://sourceware.org/git/bzip2.git "$TARGET/repo"
git -C "$TARGET/repo" checkout 962d606 # 2010/09/06 uafuzz version
