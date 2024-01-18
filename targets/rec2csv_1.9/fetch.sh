#!/bin/bash
# Date: 2022/04/16
# Version: 1.9 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/recutils/recutils-1.9.tar.gz # 2022/04/16
tar -xzf recutils-1.9.tar.gz
rm recutils-1.9.tar.gz
mv recutils-1.9 repo
