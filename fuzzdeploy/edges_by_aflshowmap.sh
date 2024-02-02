#!/bin/bash
cd $SHARED
if [ ! -f "target_args" ]; then
    echo "Error: target_args not found"
    exit 1
fi
rm -rf $AFLSHOWMAP/*
$FUZZER/repo/afl-showmap -i $(find $SHARED -name "queue") -o $AFLSHOWMAP -- $OUT/$(cat target_args)
