#!/bin/bash
set -e

export TAEGET_ARGS=${PROGRAM}/$(cat "$TARGET/target_args")
bash "$FUZZER/run.sh" | tee "$SHARED/output.log"
