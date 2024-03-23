#!/bin/bash
# Date: 2023/01/16
# Version: 2.40

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/binutils/binutils-2.40.tar.gz
tar -xzf binutils-2.40.tar.gz
rm binutils-2.40.tar.gz
mv binutils-2.40 repo
