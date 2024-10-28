#!/bin/bash
# Date: 2018/11/01
# Version: jq-1.6

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/jqlang/jq "$TARGET/repo"
git -C "$TARGET/repo" checkout jq-1.6
cd "$TARGET/repo"
git submodule update --init
