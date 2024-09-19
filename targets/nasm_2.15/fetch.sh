#!/bin/bash
# Date: 2020/06/27
# Version: 2.15

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://www.nasm.us/pub/nasm/releasebuilds/2.15/nasm-2.15.tar.gz
tar -xzf nasm-2.15.tar.gz
rm nasm-2.15.tar.gz
mv nasm-2.15 repo
