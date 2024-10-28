#!/bin/bash
# Date: 2012/02/28
# Version: 3.99.5

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://sourceforge.net/projects/lame/files/lame/3.99/lame-3.99.5.tar.gz
tar -xzf lame-3.99.5.tar.gz
rm lame-3.99.5.tar.gz
mv lame-3.99.5 repo
