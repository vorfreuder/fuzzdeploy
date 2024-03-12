import os
from multiprocessing import Process

import psutil

from . import utility
from .Builder import Builder
from .CPUAllocator import CPUAllocator


class Maker:
    @staticmethod
    def _make(WORK_DIR, DST_DIR, TOOL, CPU_RANGE, ENV, SKIP_PATHS, MODE):
        WORK_DIR_DST_DIR = os.path.join(WORK_DIR, DST_DIR)
        # check if images exist
        TARGETS = set()
        for fuzzer, target, repeat, path in utility.get_workdir_paths_by(
            WORK_DIR, "ar"
        ):
            TARGETS.add(target)
        Builder.build_imgs(FUZZERS=[TOOL], TARGETS=list(TARGETS))
        cpu_allocator = CPUAllocator(CPU_RANGE=CPU_RANGE)
        for fuzzer, target, repeat, path in utility.get_workdir_paths_by(
            WORK_DIR, "ar"
        ):
            if path in SKIP_PATHS:
                continue
            dst_path = os.path.join(WORK_DIR_DST_DIR, fuzzer, target, repeat)
            os.makedirs(dst_path, exist_ok=True)
            while True:
                cpu_id = cpu_allocator.get_free_cpu(sleep_time=1, time_out=10)
                if cpu_id:
                    break
            container_id = utility.get_cmd_res(
                f"""
        docker run \
        -itd \
        --rm \
        --volume={path}:/shared \
        --volume={dst_path}:/{DST_DIR} \
        --cap-add=SYS_PTRACE \
        --security-opt seccomp=unconfined \
        --cpuset-cpus="{cpu_id}" \
        {" ".join([f"--env={k}={v}" for k, v in ENV.items()])} \
        --network=none \
        "{TOOL}/{target}" \
        -c '${{SRC}}/run.sh'
                """
            ).strip()
            cpu_allocator.append(container_id, cpu_id)
        while len(cpu_allocator.container_id_dict) > 0:
            cpu_id = cpu_allocator.get_free_cpu(sleep_time=5, time_out=10)
            if cpu_id is None:
                continue
            container_id_dict = cpu_allocator.container_id_dict
            if len(container_id_dict) == 0:
                break
            if MODE == "ALL":
                min_container_id = min(
                    container_id_dict, key=lambda k: len(container_id_dict[k])
                )
                allocated_cpu_ls = cpu_allocator.append(min_container_id, cpu_id)
                utility.get_cmd_res(
                    f"docker update --cpuset-cpus {','.join(allocated_cpu_ls)} {min_container_id} 2>/dev/null"
                )

    @staticmethod
    def make(
        WORK_DIR, DST_DIR, TOOL, CPU_RANGE=None, ENV={}, SKIP_PATHS=[], MODE="PER"
    ):
        assert os.path.exists(WORK_DIR), f"{WORK_DIR} not exists"
        if CPU_RANGE is None:
            available_cpu_count = psutil.cpu_count()
            if available_cpu_count > 1:
                available_cpu_count -= 1
            CPU_RANGE = [str(i) for i in range(available_cpu_count)]
        else:
            CPU_RANGE = [str(i) for i in CPU_RANGE]
        p = Process(
            target=Maker._make,
            args=(WORK_DIR, DST_DIR, TOOL, CPU_RANGE, ENV, SKIP_PATHS, MODE),
        )
        p.start()
        return p
