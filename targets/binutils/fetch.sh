#!/bin/bash
# Date: 2017/03/02
# Version: 2.28 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.28.tar.gz # 2017/03/02 htfuzz version
tar -xzf binutils-2.28.tar.gz
rm binutils-2.28.tar.gz
mv binutils-2.28 repo
