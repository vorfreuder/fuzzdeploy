#!/bin/bash
# Date: 2021/04/14
# Version: 3.06.0.1

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/Matthias-Wandel/jhead "$TARGET/repo"
git -C "$TARGET/repo" checkout 3.06.0.1
