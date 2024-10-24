#!/bin/bash
# Date: 2021/07/18
# Version: 2.37

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.37.tar.gz # 2021/07/18
tar -xzf binutils-2.37.tar.gz
rm binutils-2.37.tar.gz
mv binutils-2.37 repo
