#!/bin/bash
# Date: 2020/03/04
# Version: v2.1.0

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/cisco/openh264 "$TARGET/repo"
git -C "$TARGET/repo" checkout v2.1.0
