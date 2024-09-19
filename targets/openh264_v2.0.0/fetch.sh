#!/bin/bash
# Date: 2019/05/08
# Version: v2.0.0

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/cisco/openh264 "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.0.0
