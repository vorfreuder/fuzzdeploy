#!/bin/bash
# Date: 2023/09/06
# Version: jq-1.7

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/jqlang/jq "$TARGET/repo"
git -C "$TARGET/repo" checkout jq-1.7
cd "$TARGET/repo"
git submodule update --init
