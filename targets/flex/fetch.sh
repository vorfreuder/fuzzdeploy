#!/bin/bash
# Date: 2023/11/02
# Version: 9457969 latest commit

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/westes/flex "$TARGET/repo"
git -C "$TARGET/repo" checkout 94579697864e4c33f28b8d7e97b5c599a0ca3903
