import os

from . import utility
from .Builder import Builder
from .constants import *
from .CpuAllocator import CpuAllocator
from .Maker import Maker


class EdgeAnalysis:
    @staticmethod
    def obtain(
        WORK_DIR: "str | callable",
        BASE_FUZZER,
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
            hash_file = os.path.join(
                work_dir, "aflshowmap", fuzzer, target, repeat, BASE_FUZZER, ".hash"
            )
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
            "aflshowmap",
            BASE_FUZZER,
            IS_SKIP=is_handled,
            ENV={
                "SCRIPT": "edges_by_aflshowmap.sh",
            },
        )
        maker.thread.join()
        summary_info = {}
        for work_dir, fuzzer, target, repeat, ar_path in utility.get_workdir_paths_by(
            WORK_DIR
        ):
            summary_info.setdefault(target, [])
            summary_path = os.path.join(
                work_dir,
                "aflshowmap",
                fuzzer,
                target,
                repeat,
                BASE_FUZZER,
                "summary.log",
            )
            with open(summary_path, "r", encoding="utf-8") as f:
                line_count = sum(1 for line in f)
            summary_info[target].append(
                {
                    "fuzzer": fuzzer,
                    "repeat": repeat,
                    "summary": line_count,
                }
            )
            hash_file = os.path.join(
                work_dir,
                "aflshowmap",
                fuzzer,
                target,
                repeat,
                BASE_FUZZER,
                ".hash",
            )
            queue_path = utility.search_item(ar_path, "FOLDER", "queue")
            hash_value = utility.hash_filenames(queue_path)
            with open(hash_file, "w") as f:
                f.write(hash_value)
        return summary_info
