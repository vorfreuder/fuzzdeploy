#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
./configure --disable-shared
make -j $(nproc)
sudo make install

cp bin/gcc/MP4Box "$PROGRAM"
