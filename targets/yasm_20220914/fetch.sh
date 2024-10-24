#!/bin/bash
# Date: 2022/09/14
# Version: 101bca9

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/yasm/yasm "$TARGET/repo"
git -C "$TARGET/repo" checkout 101bca9ca8ef3c07de9432dfae6e5c182ad00932
