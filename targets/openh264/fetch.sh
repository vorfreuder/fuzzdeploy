#!/bin/bash
# Date: 2019/03/04
# Version: 8684722 uafl version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/cisco/openh264 "$TARGET/repo"
git -C "$TARGET/repo" checkout 8684722271ac16118df2fe50322ffe218b9507a7 # 2019/03/04 uafl version
