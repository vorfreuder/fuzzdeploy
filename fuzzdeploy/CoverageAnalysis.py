import os
import re
import shutil
import time

from openpyxl.styles import Font, PatternFill

from . import utility
from .Builder import Builder
from .CPUAllocator import CPUAllocator
from .ExcelManager import ExcelManager


class CoverageAnalysis:
    @staticmethod
    @utility.time_count(
        "Coverage BY AFL-COV@https://github.com/vanhauser-thc/afl-cov DONE!"
    )
    def coverage_by_aflcov(WORK_DIR):
        assert os.path.exists(WORK_DIR), f"{WORK_DIR} not exists"
        WORK_DIR_COV = os.path.join(WORK_DIR, "cov")
        # check if images exist
        TARGETS = set()
        for fuzzer, target, repeat, test_path in utility.get_workdir_paths_by(WORK_DIR):
            assert os.path.exists(
                os.path.join(test_path, "target_args")
            ), f"target_args not found in {test_path}"
            TARGETS.add(target)
        Builder.build_imgs(FUZZERS=["aflcov"], TARGETS=list(TARGETS))
        cpu_allocator = CPUAllocator()
        for fuzzer, target, repeat, test_path in utility.get_workdir_paths_by(WORK_DIR):
            coverage_path = os.path.join(WORK_DIR_COV, fuzzer, target, repeat)
            coverage_log_path = os.path.join(
                WORK_DIR_COV, fuzzer, target, repeat, "afl-cov.log"
            )
            if os.path.exists(coverage_path):
                shutil.rmtree(coverage_path)
            os.makedirs(coverage_path)
            cpu_id = cpu_allocator.get_free_cpu()
            container_id = utility.get_cmd_res(
                f"""
            docker run \
            -itd \
            --rm \
            --volume={test_path}:/shared \
            --volume={coverage_path}:/cov \
            --cap-add=SYS_PTRACE \
            --security-opt seccomp=unconfined \
            --cpuset-cpus="{cpu_id}" \
            --network=none \
            "aflcov/{target}" \
            -c '${{SRC}}/line_cov_by_aflcov.sh'
                    """
            ).strip()
            cpu_allocator.append(container_id, cpu_id)
        cpu_allocator.wait_for_done()
        res = []
        for fuzzer, target, repeat, test_path in utility.get_workdir_paths_by(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            coverage_log_path = os.path.join(
                WORK_DIR_COV, fuzzer, target, repeat, "afl-cov.log"
            )
            assert os.path.exists(coverage_log_path), f"{coverage_log_path} not exists"
            coverage_log = open(coverage_log_path, "r").read()
            for line in coverage_log.split("\n"):
                if line.lstrip().startswith("lines"):
                    info = line.split(":", 1)[1].split("%", 1)[0].strip()
                    # print(f"{fuzzer} {target} {repeat} {info}")
                    res.append(
                        {
                            "fuzzer": fuzzer,
                            "target": target,
                            "linecov": info,
                        }
                    )
                    break
        return res
