#!/bin/bash
# Date: 2021/07/10
# Version: 41762be

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/yasm/yasm "$TARGET/repo"
git -C "$TARGET/repo" checkout 41762bead150fdae59687b35c8acd1c4ae0f1575
