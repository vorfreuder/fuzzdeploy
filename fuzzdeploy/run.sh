#!/bin/bash
set -e

if [ -z "$CPU_ID" ]; then
    exec bash
fi

echo $TAEGET_ARGS >$SHARED/target_args
export TAEGET_ARGS="$OUT/$TAEGET_ARGS"
timeout $TIMEOUT bash $FUZZER/run.sh | tee $SHARED/output.log
rm ${LOCK}/${CPU_ID}
# cat > ${LOCK}/${CPU_ID} << EOF
# {
#     "status": "DONE"
# }
# EOF
