#!/bin/bash
# Date: 2020/08/28
# Version: 2.15.05

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/nasm-2.15.05.tar.gz
tar -xzf nasm-2.15.05.tar.gz
rm nasm-2.15.05.tar.gz
mv nasm-2.15.05 repo
