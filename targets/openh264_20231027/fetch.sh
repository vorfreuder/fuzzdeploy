#!/bin/bash
# Date: 2023/10/27
# Version: 34e14ea latest commit

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/cisco/openh264 "$TARGET/repo"
git -C "$TARGET/repo" checkout 34e14ea # 2023/10/27
