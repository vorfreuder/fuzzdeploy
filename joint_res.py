import os
import sys

from fuzzdeploy import CasrTriageAnalysis, JointAnalysis, StateAnalysis

WORK_DIR = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.realpath(__file__)), "workdir_test")
)
STATS_FILE = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(
        os.path.dirname(WORK_DIR), f"{os.path.basename(WORK_DIR)}_fuzzer_stats.xlsx"
    )
)
# StateAnalysis.save_state_results(WORK_DIR=WORK_DIR, OUTPUT_FILE=STATS_FILE)
TRIAGE_FILE = (
    sys.argv[3]
    if len(sys.argv) > 3
    else os.path.join(
        os.path.dirname(WORK_DIR), f"{os.path.basename(WORK_DIR)}_triage_by_casr.xlsx"
    )
)
# CasrTriageAnalysis.save_triage_by_casr_results(
#     WORK_DIR=WORK_DIR, OUTPUT_FILE=TRIAGE_FILE
# )

OUTPUT_FILE = (
    sys.argv[4]
    if len(sys.argv) > 4
    else os.path.join(
        os.path.dirname(WORK_DIR), f"{os.path.basename(WORK_DIR)}_joint.xlsx"
    )
)
JointAnalysis.save_joint_results(
    STATS_FILE=STATS_FILE, TRIAGE_FILE=TRIAGE_FILE, OUTPUT_FILE=OUTPUT_FILE
)
