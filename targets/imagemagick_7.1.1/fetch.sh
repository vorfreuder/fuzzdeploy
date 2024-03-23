#!/bin/bash
# Date: 2023/10/21
# Version: 7.1.1-21 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://imagemagick.org/archive/releases/ImageMagick-7.1.1-21.tar.xz # 2023/10/21
tar -xJf ImageMagick-7.1.1-21.tar.xz
rm ImageMagick-7.1.1-21.tar.xz
mv ImageMagick-7.1.1-21 repo
