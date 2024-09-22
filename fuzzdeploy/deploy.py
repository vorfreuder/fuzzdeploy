import datetime
import os
import signal
import time
from functools import partial
from pathlib import Path

import docker
from docker.models.containers import Container

from .utils import (
    get_free_cpu,
    get_target_image_name,
    is_image_exist,
    remove_exited_container,
)


def sigint_handler(signal, frame, container_ls):
    print("SIGINT received, stopping all containers")
    for container in container_ls:
        container.stop()
        container.remove()
    import sys

    sys.exit(1)


def _get_idx(path: str | Path) -> int:
    path = Path(path)
    if not path.exists():
        return 1
    idx = [1]
    for p in path.iterdir():
        if p.is_dir() and p.name.isdigit():
            idx.append(int(p.name))
    return max(idx) + 1


def fuzzing(
    work_dir: str | Path,
    fuzzers: list[str],
    targets: list[str],
    timeout: str,
    repeat: int = 1,
    *,
    cpu_range: (list[str | int] | set[str | int]) | None = None,
):
    assert work_dir, "work_dir should not be None"
    work_dir = Path(work_dir).absolute()
    assert fuzzers and len(fuzzers) > 0, "fuzzers should contain one element at least"
    assert targets and len(targets) > 0, "targets should contain one element at least"
    assert timeout, "timeout should not be None"
    if cpu_range is not None:
        cpu_range = [str(i) for i in cpu_range]
    else:
        cpu_range = set(
            [str(i) for i in range(int(docker.from_env().info().get("NCPU")))]
        )
    assert cpu_range, "cpu_range should contain one element at least"
    # check if the images exist
    for fuzzer in fuzzers:
        for target in targets:
            target_image_name = get_target_image_name(fuzzer, target)
            assert is_image_exist(
                target_image_name
            ), f"docker image {target_image_name} not found"

    container_ls: list[Container] = []
    signal.signal(signal.SIGINT, partial(sigint_handler, container_ls=container_ls))
    for repeat_idx in range(repeat):
        for fuzzer in fuzzers:
            for target in targets:
                cpu_id = get_free_cpu(container_ls, cpu_range)  # type: ignore
                while cpu_id is None:
                    time.sleep(10)
                    remove_exited_container(container_ls)
                    cpu_id = get_free_cpu(container_ls, cpu_range)  # type: ignore
                base_path = work_dir / "archive" / fuzzer / target
                idx = str(_get_idx(base_path))
                host_path = base_path / idx
                host_path.mkdir(parents=True)
                container = docker.from_env().containers.run(
                    image=get_target_image_name(fuzzer, target),
                    command=f"-c 'timeout {timeout} ${{SRC}}/script.sh'",
                    cap_add=["SYS_PTRACE"],
                    cpuset_cpus=cpu_id,
                    detach=True,
                    name=f"{fuzzer}-{target}-{idx}",
                    network_mode="none",
                    privileged=True,
                    tty=True,
                    security_opt=["seccomp=unconfined"],
                    volumes={
                        host_path.as_posix(): {"bind": "/shared", "mode": "rw"},
                        (Path(__file__).parent.absolute() / "start.sh").as_posix(): {
                            "bind": "/src/script.sh",
                            "mode": "ro",
                        },
                    },  # type: ignore
                    labels={
                        "fuzzer": fuzzer,
                        "target": target,
                        "idx": idx,
                    },
                    user=f"{os.getuid()}:{os.getgid()}",
                )
                container_ls.append(container)
                print(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    container.short_id,
                    fuzzer.ljust(16),
                    target.ljust(10),
                    str(repeat_idx).ljust(3),
                    "starts on cpu",
                    cpu_id,
                )
    for container in container_ls:
        container.wait()
        container.remove()
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} DONE")
    print(f"The results can be found in {work_dir/'archive'}")
