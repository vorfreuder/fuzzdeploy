#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
autoreconf -i
./configure
make -j $(nproc)

cp jq "$PROGRAM"
