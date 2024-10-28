#!/bin/bash
set -e

export AFL_SKIP_CPUFREQ=1
export AFL_NO_AFFINITY=1

cd "$PROGRAM"
"$FUZZER/repo/bb_metric/afl-fuzz" -s -m none -t 2000+ \
    -i "$TARGET/corpus" -o "$SHARED" \
    $FUZZER_ARGS -- $TAEGET_ARGS
