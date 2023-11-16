#!/bin/bash
# Date: 2018/11/07
# Version: 2.14 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://www.nasm.us/pub/nasm/releasebuilds/2.14/nasm-2.14.tar.gz # 2018/11/07 htfuzz version
tar -xzf nasm-2.14.tar.gz
rm nasm-2.14.tar.gz
mv nasm-2.14 repo
