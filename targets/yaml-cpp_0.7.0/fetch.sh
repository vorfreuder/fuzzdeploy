#!/bin/bash
# Date: 2021/07/10
# Version: yaml-cpp-0.7.0

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/jbeder/yaml-cpp "$TARGET/repo"
git -C "$TARGET/repo" checkout yaml-cpp-0.7.0
