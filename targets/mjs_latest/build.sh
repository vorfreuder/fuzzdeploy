#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
$CC $CFLAGS -DMJS_MAIN mjs.c -o mjs

cp mjs "$PROGRAM"
