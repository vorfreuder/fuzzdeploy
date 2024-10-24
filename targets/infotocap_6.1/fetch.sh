#!/bin/bash
# Date: 2018/01/27
# Version: 6.1
set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"

wget -nc -v https://invisible-mirror.net/archives/ncurses/ncurses-6.1.tar.gz && tar -xzf ncurses-6.1.tar.gz
rm ncurses-6.1.tar.gz
mv ncurses-6.1 repo
