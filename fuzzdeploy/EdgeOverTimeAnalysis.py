import csv
import json
import os
import shutil

from . import utility
from .Builder import Builder
from .constants import *
from .CpuAllocator import CpuAllocator
from .Maker import Maker


class EdgeOverTimeAnalysis:
    @staticmethod
    def get_csv_data(file_path):
        queue_to_time = {}
        last_index = 0
        base_time = None
        with open(
            file_path,
            newline="",
        ) as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                relative_time = None
                queue_index = None
                for key, val in row.items():
                    if "unix_time" in key or "relative_time" in key:
                        relative_time = int(val)
                        if "unix_time" in key:
                            if not base_time:
                                base_time = relative_time
                                relative_time = 0
                            else:
                                relative_time -= base_time
                    if "paths_total" in key or "corpus_count" in key:
                        queue_index = int(val)
                assert (
                    relative_time is not None and queue_index is not None
                ), "invalid row"
                if queue_index > last_index:
                    last_index = queue_index
                    queue_to_time[queue_index] = relative_time
        return queue_to_time

    @staticmethod
    def obtain(WORK_DIR, BASE_FUZZER, TIME_RANGE, INTERVAL):
        for work_dir, fuzzer, target, repeat, ar_path in utility.get_workdir_paths_by(
            WORK_DIR
        ):
            assert os.path.exists(
                os.path.join(ar_path, "target_args")
            ), f"target_args not found in {ar_path}"
            queue_path = utility.search_item(ar_path, "FOLDER", "queue")
            assert queue_path, f"IMPOSSIBLE! queue folder not found in {ar_path}"
        TIME_RANGE = int(TIME_RANGE)
        INTERVAL = int(INTERVAL)

        def is_handled(fuzzer, target, repeat, dst_path, work_dir):
            base_path = os.path.join(dst_path, BASE_FUZZER)
            edges_path = os.path.join(base_path, "edges")
            ar_path = os.path.join(work_dir, "ar", fuzzer, target, repeat)
            queue_path = utility.search_item(ar_path, "FOLDER", "queue")
            if not os.path.exists(edges_path):
                return False
            edges_path_files = set(os.listdir(edges_path))
            queue_path_files = set(
                [
                    _
                    for _ in os.listdir(queue_path)
                    if _.startswith("id:")
                    and os.path.isfile(os.path.join(queue_path, _))
                ]
            )
            diff_set = edges_path_files.difference(queue_path_files)
            for _ in diff_set:
                os.remove(os.path.join(edges_path, _))
                edges_path_files.remove(_)
            diff_set = queue_path_files.difference(edges_path_files)
            edges_over_seeds_path = os.path.join(
                base_path,
                "edges_over_seeds.log",
            )
            if len(diff_set) == 0 and os.path.exists(edges_over_seeds_path):
                return True
            return False

        maker = Maker(
            WORK_DIR,
            "aflshowmap_overtime",
            BASE_FUZZER,
            IS_SKIP=is_handled,
            ENV={
                "SCRIPT": "edges_by_aflshowmap_overtime.py",
            },
            MODE="ALL",
        )
        maker.thread.join()
        # edges calculation done
        edge_over_time_info = {}
        for work_dir, fuzzer, target, repeat, ar_path in utility.get_workdir_paths_by(
            WORK_DIR
        ):
            edge_over_time_info.setdefault(target, [])
            edges_over_seeds_path = os.path.join(
                work_dir,
                "aflshowmap_overtime",
                fuzzer,
                target,
                repeat,
                BASE_FUZZER,
                "edges_over_seeds.log",
            )
            with open(edges_over_seeds_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                edges_over_seeds = {
                    int(key): value for key, value in loaded_data.items()
                }
            plot_data_path = utility.search_item(ar_path, "FILE", PLOT_DATA)
            assert plot_data_path, f"{plot_data_path} not exists"
            queue_to_time = EdgeOverTimeAnalysis.get_csv_data(plot_data_path)
            edge_over_time = {}
            for i in range(0, TIME_RANGE + INTERVAL, INTERVAL):
                edge_over_time[i] = 0
            id_ls = sorted(queue_to_time.keys())
            id_index = 0
            if queue_to_time[id_ls[id_index]] <= TIME_RANGE:
                for i in range(INTERVAL, TIME_RANGE + INTERVAL, INTERVAL):
                    while (
                        id_index + 1 < len(id_ls)
                        and i >= queue_to_time[id_ls[id_index + 1]]
                        and id_ls[id_index + 1] in edges_over_seeds
                    ):
                        id_index += 1
                    if id_index == 0 and id_ls[id_index] not in edges_over_seeds:
                        continue
                    edge_over_time[i] = edges_over_seeds[id_ls[id_index]]
            edge_over_time_info[target].append(
                {
                    "fuzzer": fuzzer,
                    "repeat": repeat,
                    "edge_over_time": edge_over_time,
                }
            )
        return edge_over_time_info
