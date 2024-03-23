import os
import sys

from fuzzdeploy import BugFoundByTimeAnalysis

WORK_DIR = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.realpath(__file__)), "workdir_test")
)
OUTPUT_FILE = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(
        WORK_DIR,
        f"{os.path.basename(WORK_DIR)}_bug_found_by_time.xlsx",
    )
)
BugFoundByTimeAnalysis.save(WORK_DIR=WORK_DIR, OUTPUT_FILE=OUTPUT_FILE)
