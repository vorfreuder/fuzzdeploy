#!/bin/bash
# Date: 2023/06/07
# Version: 3.08

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/Matthias-Wandel/jhead "$TARGET/repo"
git -C "$TARGET/repo" checkout 3.08
