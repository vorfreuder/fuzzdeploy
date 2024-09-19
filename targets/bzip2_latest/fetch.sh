#!/bin/bash
# Date: 2022/05/26
# Version: 9de658d latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone git://sourceware.org/git/bzip2.git "$TARGET/repo"
git -C "$TARGET/repo" checkout 9de658d248f9fd304afa3321dd7a9de1280356ec
