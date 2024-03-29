#!/bin/bash
set -e

if [ -n "$DST" ]; then
    if [ -n "$SCRIPT" ]; then
        $SRC/scripts/$SCRIPT
        exit 0
    fi
    bash $FUZZER/run.sh
    exit 0
fi

if [ -z "$CPU_ID" ]; then
    exec bash
fi

echo $TAEGET_ARGS >$SHARED/target_args
export TAEGET_ARGS="$OUT/$TAEGET_ARGS"
timeout $TIMEOUT bash $FUZZER/run.sh | tee $SHARED/output.log
