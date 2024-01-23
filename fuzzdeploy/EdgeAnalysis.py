import os
import re
import shutil
import time

from openpyxl.styles import Font, PatternFill

from . import utility
from .Builder import Builder
from .CPUAllocator import CPUAllocator
from .ExcelManager import ExcelManager


class EdgeAnalysis:
    @staticmethod
    def edges_by_aflshowmap(WORK_DIR, FUZZER):
        assert os.path.exists(WORK_DIR), f"{WORK_DIR} not exists"
        WORK_DIR_AFLSHOWMAP = os.path.join(WORK_DIR, "aflshowmap")
        # check if images exist
        TARGETS = set()
        for test_path in utility.test_paths(WORK_DIR):
            assert os.path.exists(
                os.path.join(test_path, "target_args")
            ), f"target_args not found in {test_path}"
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            TARGETS.add(target)
        Builder.build_imgs(FUZZERS=[FUZZER], TARGETS=list(TARGETS))
        cpu_allocator = CPUAllocator()
        for test_path in utility.test_paths(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            edges_path = os.path.join(WORK_DIR_AFLSHOWMAP, fuzzer, target, repeat)
            os.makedirs(edges_path, exist_ok=True)
            cpu_id = cpu_allocator.get_free_cpu()
            container_id = utility.get_cmd_res(
                f"""
            docker run \
            -itd \
            --rm \
            --volume={test_path}:/shared \
            --volume={edges_path}:/aflshowmap \
            --cap-add=SYS_PTRACE \
            --security-opt seccomp=unconfined \
            --cpuset-cpus="{cpu_id}" \
            --network=none \
            "{FUZZER}/{target}" \
            -c '${{SRC}}/edges_by_aflshowmap.sh'
                    """
            ).strip()
            cpu_allocator.append(container_id, cpu_id)
        cpu_allocator.wait_for_done()
        for test_path in utility.test_paths(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            aflshowmap_log_path = os.path.join(
                WORK_DIR_AFLSHOWMAP, fuzzer, target, repeat, "afl-showmap.log"
            )
            assert os.path.exists(
                aflshowmap_log_path
            ), f"{aflshowmap_log_path} not exists"
            aflshowmap_log = open(aflshowmap_log_path, "r").read()
            for line in aflshowmap_log.split("\n"):
                if "edges" in line:
                    line = re.findall(r"\d+ edges", line)[0]
                    print(f"{fuzzer} {target} {repeat} {line}")
                    break
