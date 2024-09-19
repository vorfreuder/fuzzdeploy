#!/bin/bash
# Date: 2019/10/06
# Version: 7.0.8-68 htfuzz version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://imagemagick.org/archive/releases/ImageMagick-7.0.8-68.tar.xz # 2019/10/06 htfuzz version
tar -xJf ImageMagick-7.0.8-68.tar.xz
rm ImageMagick-7.0.8-68.tar.xz
mv ImageMagick-7.0.8-68 repo
