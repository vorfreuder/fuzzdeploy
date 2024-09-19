#!/bin/bash
# Date: 2022/03/10
# Version:  v4.2.0

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/VirusTotal/yara "$TARGET/repo"
git -C "$TARGET/repo" checkout v4.2.0
