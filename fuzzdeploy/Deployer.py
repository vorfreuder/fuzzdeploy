import datetime
import os
import signal
import sys
import time

import psutil

from . import utility


class Deployer:
    def __init__(
        self,
        WORK_DIR,
        FUZZERS,
        TARGETS,
        TIMEOUT,
        FUZZERS_ARGS,
        REPEAT=1,
        CPU_RANGE=None,
    ) -> None:
        assert WORK_DIR is not None, "WORK_DIR should not be None"
        assert FUZZERS is not None, "FUZZERS should not be None"
        assert TARGETS is not None, "TARGETS should not be None"
        assert TIMEOUT is not None, "TIMEOUT should not be None"
        assert FUZZERS_ARGS is not None, "FUZZERS_ARGS should not be None"
        self.WORK_DIR = os.path.abspath(WORK_DIR)
        self.WORK_DIR_AR = os.path.join(self.WORK_DIR, "ar")
        self.WORK_DIR_LOCK = os.path.join(self.WORK_DIR, "lock")
        self.FUZZERS = FUZZERS
        self.TARGETS = TARGETS
        self.TIMEOUT = TIMEOUT
        self.FUZZERS_ARGS = FUZZERS_ARGS
        if not isinstance(REPEAT, (list, tuple)):
            REPEAT = [REPEAT]
        self.REPEAT = [str(i) for i in REPEAT]
        if CPU_RANGE is not None:
            self.CPU_RANGE = [str(i) for i in CPU_RANGE]
        else:
            self.CPU_RANGE = [str(i) for i in range(psutil.cpu_count())]

    def init_workdir(self):
        WORK_DIR = self.WORK_DIR
        WORK_DIR_AR = self.WORK_DIR_AR
        WORK_DIR_LOCK = self.WORK_DIR_LOCK
        FUZZERS = self.FUZZERS
        TARGETS = self.TARGETS
        REPEAT = self.REPEAT
        os.makedirs(WORK_DIR_LOCK, exist_ok=True)
        for fuzzer in FUZZERS:
            for target in TARGETS.keys():
                os.makedirs(os.path.join(WORK_DIR_AR, fuzzer, target), exist_ok=True)
                for index in REPEAT:
                    assert not os.path.exists(
                        os.path.join(WORK_DIR_AR, fuzzer, target, index)
                    ), f"{os.path.join(WORK_DIR_AR, fuzzer, target, index)} already exists, remove it or change REPEAT"
                    os.mkdir(os.path.join(WORK_DIR_AR, fuzzer, target, index))
        utility.console.print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {WORK_DIR} init"
        )

    def cpu_allocate(self):
        CPU_RANGE = self.CPU_RANGE
        WORK_DIR_LOCK = self.WORK_DIR_LOCK
        while True:
            assert len(CPU_RANGE) > 0, "CPU_RANGE should contain one element at least"
            used_cpu_ls = os.listdir(WORK_DIR_LOCK)
            for cpu_id in CPU_RANGE:
                if cpu_id not in used_cpu_ls:
                    with open(os.path.join(WORK_DIR_LOCK, cpu_id), "x") as file:
                        pass
                    return cpu_id
            time.sleep(5)

    @utility.time_count("Fuzzing done")
    def start(self):
        WORK_DIR = self.WORK_DIR
        WORK_DIR_AR = self.WORK_DIR_AR
        WORK_DIR_LOCK = self.WORK_DIR_LOCK
        FUZZERS = self.FUZZERS
        TARGETS = self.TARGETS
        REPEAT = self.REPEAT
        TIMEOUT = self.TIMEOUT
        FUZZERS_ARGS = self.FUZZERS_ARGS
        for fuzzer in FUZZERS:
            for target in TARGETS.keys():
                assert (
                    utility.get_cmd_res(
                        f"docker images {fuzzer}/{target} | wc -l"
                    ).strip()
                    == "2"
                ), utility.console.print(f"docker image {fuzzer}/{target} not found")
        container_id_ls = []

        def sigint_handler(signal, frame):
            utility.console.print()
            with utility.console.status(
                f"[bold green]interrupted by user, docker containers removing...",
                spinner="arrow3",
            ) as status:
                for container_id in container_id_ls:
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
                    cpu_id = self.cpu_allocate()
                    container_id = utility.get_cmd_res(
                        f"""
        docker run \
        -itd \
        --rm \
        --volume={os.path.join(WORK_DIR_AR, fuzzer, target, index)}:/shared \
        --volume={WORK_DIR_LOCK}:/lock \
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
                    container_id_ls.append(container_id)
                    utility.console.print(
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        container_id[:12].ljust(12),
                        fuzzer.ljust(16),
                        target.ljust(10),
                        index.ljust(3),
                        "starts on cpu",
                        cpu_id,
                    )
        for container_id in container_id_ls:
            utility.get_cmd_res(f"docker wait {container_id} 2> /dev/null")
        utility.console.print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} All DONE!"
        )
        utility.console.print(f"The results can be found in {WORK_DIR_AR}")
