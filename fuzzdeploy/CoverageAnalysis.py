import os
import re
import shutil
import time

from openpyxl.styles import Font, PatternFill

from . import utility
from .Builder import Builder
from .CpuAllocator import CpuAllocator
from .ExcelManager import ExcelManager
from .Maker import Maker


class CoverageAnalysis:
    @staticmethod
    @utility.time_count(
        "Coverage BY AFL-COV@https://github.com/vanhauser-thc/afl-cov DONE!"
    )
    def coverage_by_aflcov(WORK_DIR):
        maker = Maker(
            WORK_DIR,
            "cov",
            "aflcov",
        )
        maker.thread.join()
        res = []
        for fuzzer, target, repeat, test_path in utility.get_workdir_paths_by(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            coverage_log_path = os.path.join(
                WORK_DIR, "cov", fuzzer, target, repeat, "afl-cov.log"
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
