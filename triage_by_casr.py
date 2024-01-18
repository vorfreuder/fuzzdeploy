import os
import sys

from fuzzdeploy import CasrTriageAnalysis

WORK_DIR = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.realpath(__file__)), "workdir_test")
)
OUTPUT_FILE = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(
        os.path.dirname(WORK_DIR), f"{os.path.basename(WORK_DIR)}_triage_by_casr.xlsx"
    )
)

CasrTriageAnalysis.fuzzer_colors = {
    "aflplusplus": "00A0B0",
    "htfuzz": "FBD26A",
}
CasrTriageAnalysis.save_triage_by_casr_results(
    WORK_DIR=WORK_DIR, OUTPUT_FILE=OUTPUT_FILE
)
