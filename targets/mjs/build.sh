#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
cd mjs
make clean all DOCKER_CLANG="$CC"

cp build/mjs "$OUT"
