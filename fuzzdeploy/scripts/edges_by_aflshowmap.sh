#!/bin/bash
cd $SHARED
if [ ! -f "target_args" ]; then
    echo "Error: target_args not found"
    exit 1
fi
export DST="$DST/$(basename $FUZZER)"
mkdir -p $DST
rm -rf $DST/summary.log
$FUZZER/repo/afl-showmap -t 3000 -q -C -i $(find $SHARED -name "queue") -o "$DST/summary.log" -- $OUT/$(cat target_args)
