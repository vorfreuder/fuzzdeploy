#!/bin/bash
# Date: 2023/09/24
# Version: 1.3.42 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://jaist.dl.sourceforge.net/project/graphicsmagick/graphicsmagick/1.3.42/GraphicsMagick-1.3.42.tar.xz
tar -xvf GraphicsMagick-1.3.42.tar.xz
rm GraphicsMagick-1.3.42.tar.xz
mv GraphicsMagick-1.3.42 repo
