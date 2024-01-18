#!/bin/bash
# Date: 2022/12/21
# Version: 2.16.01 latest stable version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://www.nasm.us/pub/nasm/releasebuilds/2.16.01/nasm-2.16.01.tar.gz # 2022/12/21
tar -xzf nasm-2.16.01.tar.gz
rm nasm-2.16.01.tar.gz
mv nasm-2.16.01 repo
