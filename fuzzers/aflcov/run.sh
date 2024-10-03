#!/bin/bash
set -e

target_args=${PROGRAM}/$(cat "$TARGET/target_args")
rm -rf $DST/*
cd $TARGET/repo
afl-cov.sh -c $SHARED "$target_args"
find $SHARED -maxdepth 2 -type d -name 'cov' -exec sh -c 'mv "$0"/* "$DST"/' {} \; -exec rm -r {} \;
