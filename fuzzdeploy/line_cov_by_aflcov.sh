#!/bin/bash
cd $TARGET/repo
afl-cov.sh -c $SHARED "$OUT/$TAEGET_ARGS"
find $SHARED -maxdepth 2 -type d -name 'cov' -exec sh -c 'mv "$0"/* "$COV"/' {} \; -exec rm -r {} \;
