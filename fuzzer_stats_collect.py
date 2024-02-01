import os
import sys

from fuzzdeploy import StateAnalysis

WORK_DIR = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.realpath(__file__)), "workdir_test")
)
OUTPUT_FILE = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(WORK_DIR, f"{os.path.basename(WORK_DIR)}_fuzzer_stats.xlsx")
)
StateAnalysis.fuzzer_colors = {
    "afl": "FBD26A",
    "aflplusplus": "00A0B0",
}
StateAnalysis.save(WORK_DIR=WORK_DIR, OUTPUT_FILE=OUTPUT_FILE)
