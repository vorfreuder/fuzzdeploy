#!/bin/bash
# Date: 2023/09/15
# Version:  v4.4.0 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/VirusTotal/yara "$TARGET/repo"
git -C "$TARGET/repo" checkout v4.4.0 # 2023/09/15
