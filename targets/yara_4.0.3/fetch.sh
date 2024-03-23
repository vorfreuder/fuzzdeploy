#!/bin/bash
# Date: 2021/01/27
# Version:  v4.0.3

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/VirusTotal/yara "$TARGET/repo"
git -C "$TARGET/repo" checkout v4.0.3
