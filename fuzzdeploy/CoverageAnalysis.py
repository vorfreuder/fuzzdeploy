import os

from . import utility
from .Builder import Builder
from .constants import *
from .CpuAllocator import CpuAllocator
from .Maker import Maker


class CoverageAnalysis:
    @staticmethod
    @utility.time_count(
        "Coverage BY AFL-COV@https://github.com/vanhauser-thc/afl-cov DONE!"
    )
    def obtain(
        WORK_DIR: "str | callable",
    ):
        for work_dir, fuzzer, target, repeat, ar_path in utility.get_workdir_paths_by(
            WORK_DIR
        ):
            assert os.path.exists(
                os.path.join(ar_path, "target_args")
            ), f"target_args not found in {ar_path}"
            queue_path = utility.search_item(ar_path, "FOLDER", "queue")
            assert queue_path, f"IMPOSSIBLE! queue folder not found in {ar_path}"

        # compute data
        def is_handled(fuzzer, target, repeat, dst_path, work_dir):
            ar_path = os.path.join(work_dir, "ar", fuzzer, target, repeat)
            hash_file = os.path.join(work_dir, "cov", fuzzer, target, repeat, ".hash")
            if not os.path.exists(hash_file):
                return False
            with open(hash_file, "r") as f:
                dst_hash = f.read()
            queue_path = utility.search_item(ar_path, "FOLDER", "queue")
            queue_hash = utility.hash_filenames(queue_path)
            if dst_hash == queue_hash:
                return True
            os.remove(hash_file)
            return False

        maker = Maker(
            WORK_DIR,
            "cov",
            "aflcov",
            IS_SKIP=is_handled,
        )
        maker.thread.join()
        summary_info = {}
        for work_dir, fuzzer, target, repeat, ar_path in utility.get_workdir_paths_by(
            WORK_DIR
        ):
            summary_info.setdefault(target, [])
            coverage_log_path = os.path.join(
                WORK_DIR, "cov", fuzzer, target, repeat, "afl-cov.log"
            )
            assert os.path.exists(coverage_log_path), f"{coverage_log_path} not exists"
            coverage_log = open(coverage_log_path, "r").read()
            for line in coverage_log.split("\n"):
                if line.lstrip().startswith("lines"):
                    info = line.split(":", 1)[1].split("%", 1)[0].strip()
                    # print(f"{fuzzer} {target} {repeat} {info}")
                    summary_info[target].append(
                        {
                            "fuzzer": fuzzer,
                            "linecov": info,
                        }
                    )
                    break
            hash_file = os.path.join(
                work_dir,
                "cov",
                fuzzer,
                target,
                repeat,
                ".hash",
            )
            if not os.path.exists(hash_file):
                queue_path = utility.search_item(ar_path, "FOLDER", "queue")
                hash_value = utility.hash_filenames(queue_path)
                with open(hash_file, "w") as f:
                    f.write(hash_value)
        return summary_info
