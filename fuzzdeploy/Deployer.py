import datetime
import os
import signal
import sys
import time

import psutil

from . import utility
from .CpuAllocator import CpuAllocator


class Deployer:
    @staticmethod
    @utility.time_count("Fuzzing done")
    def start_fuzzing(
        WORK_DIR, FUZZERS, TARGETS, TIMEOUT, FUZZERS_ARGS, REPEAT=1, CPU_RANGE=None
    ):
        assert WORK_DIR is not None, "WORK_DIR should not be None"
        assert FUZZERS is not None, "FUZZERS should not be None"
        assert TARGETS is not None, "TARGETS should not be None"
        assert TIMEOUT is not None, "TIMEOUT should not be None"
        if FUZZERS_ARGS is None:
            FUZZERS_ARGS = {}
            for fuzzer in FUZZERS:
                FUZZERS_ARGS[fuzzer] = {}
                for target in TARGETS.keys():
                    FUZZERS_ARGS[fuzzer][target] = ""
        WORK_DIR = os.path.abspath(WORK_DIR)
        WORK_DIR_AR = os.path.join(WORK_DIR, "ar")
        if not isinstance(REPEAT, (list, tuple)):
            REPEAT = [REPEAT]
        REPEAT = [str(i) for i in REPEAT]
        if CPU_RANGE is not None:
            CPU_RANGE = [str(i) for i in CPU_RANGE]
        else:
            CPU_RANGE = [str(i) for i in range(psutil.cpu_count())]
        assert len(CPU_RANGE) > 0, "CPU_RANGE should contain one element at least"
        # init_workdir
        for fuzzer in FUZZERS:
            for target in TARGETS.keys():
                for index in REPEAT:
                    path = os.path.join(WORK_DIR_AR, fuzzer, target, index)
                    assert not os.path.exists(
                        path
                    ), f"{path} already exists, remove it or change REPEAT"
                    os.makedirs(path)
        utility.console.print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {WORK_DIR} init"
        )
        # start fuzzing
        for fuzzer in FUZZERS:
            for target in TARGETS.keys():
                assert (
                    utility.get_cmd_res(
                        f'docker images --format "{{{{.Repository}}}}" | grep -q "^{fuzzer}/{target}"'
                    )
                    != None
                ), utility.console.print(f"docker image {fuzzer}/{target} not found")

        cpu_allocator = CpuAllocator(CPU_RANGE)

        def sigint_handler(signal, frame):
            utility.console.print()
            with utility.console.status(
                f"[bold green]interrupted by user, docker containers removing...",
                spinner="arrow3",
            ) as status:
                for container_id in cpu_allocator.container_id_dict.keys():
                    utility.get_cmd_res(f"docker rm -f {container_id}")
            utility.console.print(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} interrupted by user, \
docker containers removed"
            )
            utility.console.print(f"The results can be found in {WORK_DIR_AR}")
            sys.exit()

        signal.signal(signal.SIGINT, sigint_handler)
        for index in REPEAT:
            for fuzzer in FUZZERS:
                for target in TARGETS.keys():
                    cpu_id = cpu_allocator.get_free_cpu()
                    container_id = utility.get_cmd_res(
                        f"""
        docker run \
        -itd \
        --rm \
        --volume={os.path.join(WORK_DIR_AR, fuzzer, target, index)}:/shared \
        --cap-add=SYS_PTRACE \
        --security-opt seccomp=unconfined \
        --cpuset-cpus="{cpu_id}" \
        --env=CPU_ID={cpu_id} \
        --env=FUZZER_ARGS="{FUZZERS_ARGS[fuzzer][target]}" \
        --env=TAEGET_ARGS="{TARGETS[target]}" \
        --env=TIMEOUT="{TIMEOUT}" \
        --network=none \
        --privileged \
        "{fuzzer}/{target}" \
        -c '${{SRC}}/run.sh'
                        """
                    ).strip()
                    cpu_allocator.append(container_id, cpu_id)
                    utility.console.print(
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        container_id[:12].ljust(12),
                        fuzzer.ljust(16),
                        target.ljust(10),
                        index.ljust(3),
                        "starts on cpu",
                        cpu_id,
                    )
        cpu_allocator.wait_for_done()
        utility.console.print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} All DONE!"
        )
        utility.console.print(f"The results can be found in {WORK_DIR_AR}")
