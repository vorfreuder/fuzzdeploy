#!/bin/bash
# Date: 2018/03/31
# Version: RELEASE.1.4.5 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/tjko/jpegoptim "$TARGET/repo"
git -C "$TARGET/repo" checkout RELEASE.1.4.5 # 2018/03/31 htfuzz version
