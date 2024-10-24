#!/bin/bash
# Date: 2023/07/30
# Version: 2.41 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.41.tar.gz # 2023/07/30
tar -xzf binutils-2.41.tar.gz
rm binutils-2.41.tar.gz
mv binutils-2.41 repo
