#!/bin/bash
# Date: 2021/01/24
# Version: 2.36

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.36.tar.gz # 2021/01/24
tar -xzf binutils-2.36.tar.gz
rm binutils-2.36.tar.gz
mv binutils-2.36 repo
