#!/bin/bash
cd $SHARED
if [ ! -f "target_args" ]; then
    echo "Error: target_args not found"
    exit 1
fi
target_args="$OUT/$(cat target_args)"
cd $TARGET/repo
afl-cov.sh -c $SHARED "$target_args"
find $SHARED -maxdepth 2 -type d -name 'cov' -exec sh -c 'mv "$0"/* "$COV"/' {} \; -exec rm -r {} \;
