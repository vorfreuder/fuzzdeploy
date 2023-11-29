#!/bin/bash
# Date: 2020/02/01
# Version: 2.34

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.34.tar.gz
tar -xzf binutils-2.34.tar.gz
rm binutils-2.34.tar.gz
mv binutils-2.34 repo
