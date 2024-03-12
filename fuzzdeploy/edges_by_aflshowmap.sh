#!/bin/bash
cd $SHARED
if [ ! -f "target_args" ]; then
    echo "Error: target_args not found"
    exit 1
fi
rm -rf $AFLSHOWMAP/summary.log
$FUZZER/repo/afl-showmap -t 3000 -q -C -i $(find $SHARED -name "queue") -o "$AFLSHOWMAP/summary.log" -- $OUT/$(cat target_args)
