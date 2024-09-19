#!/bin/bash
# Date: 2018/03/05
# Version: yaml-cpp-0.6.2 memlock version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

git clone https://github.com/jbeder/yaml-cpp "$TARGET/repo"
git -C "$TARGET/repo" checkout yaml-cpp-0.6.2
