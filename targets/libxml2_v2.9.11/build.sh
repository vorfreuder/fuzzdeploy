#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
export ACLOCAL_PATH=/usr/share/aclocal
export ASAN_OPTIONS=detect_leaks=0 # Centos7 needs
./autogen.sh --with-http=no --with-python=no --with-lzma=yes --with-threads=no --disable-shared
make -j $(nproc)

cp xmllint "$OUT"
