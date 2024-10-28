#!/bin/bash
# Date: 2017/10/13
# Version: 3.100

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://sourceforge.net/projects/lame/files/lame/3.100/lame-3.100.tar.gz
tar -xzf lame-3.100.tar.gz
rm lame-3.100.tar.gz
mv lame-3.100 repo
