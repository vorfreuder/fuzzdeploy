#!/bin/bash
# Date: 2017/07/04
# Version: 1.3.26 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
git clone --depth 1 https://github.com/sharedata21/HTFuzz
mv HTFuzz/program/GraphicsMagick/code "$TARGET/repo" # 2017/07/04 htfuzz version
rm -rf HTFuzz
