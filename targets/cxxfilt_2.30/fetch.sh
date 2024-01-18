#!/bin/bash
# Date: 2018/01/28
# Version: 2.30

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.30.tar.gz
tar -xzf binutils-2.30.tar.gz
rm binutils-2.30.tar.gz
mv binutils-2.30 repo
