#!/bin/bash
# Date: 2022/02/09
# Version: 2.38

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.38.tar.gz
tar -xzf binutils-2.38.tar.gz
rm binutils-2.38.tar.gz
mv binutils-2.38 repo
