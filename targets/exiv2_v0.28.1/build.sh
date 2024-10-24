#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
rm -rf build
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DEXIV2_ENABLE_INIH=OFF
cmake --build build -j $(nproc)

cp build/bin/exiv2 "$PROGRAM"
