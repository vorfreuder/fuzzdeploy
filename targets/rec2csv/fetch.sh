#!/bin/bash
# Date: 2019/01/03
# Version: 1.8 uafuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/recutils/recutils-1.8.tar.gz # 2019/01/03 uafuzz version
tar -xzf recutils-1.8.tar.gz
rm recutils-1.8.tar.gz
mv recutils-1.8 repo
