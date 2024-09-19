#!/bin/bash
set -e

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
export SOURCE_DIR="$TARGET/repo"
export BUILD_DIR="$TARGET/repo/build_dir"
export INSTALL_DIR="$TARGET/repo/install_dir"
cmake -H$SOURCE_DIR -B$BUILD_DIR -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR
cmake --build $BUILD_DIR -j $(nproc)

cp $BUILD_DIR/src/app/jasper "$PROGRAM"
