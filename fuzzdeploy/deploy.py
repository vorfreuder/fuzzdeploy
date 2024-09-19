import datetime
import signal
import time
from pathlib import Path

import docker
from docker.errors import NotFound

from .utils import get_target_image_name, is_image_exist

OWNER = str(datetime.datetime.now())


def get_containers():
    container_ls = []
    for container in docker.from_env().containers.list():
        if container.labels.get("owner") == OWNER:
            container_ls.append(container)
    return container_ls


def sigint_handler(signal, frame):
    print("SIGINT received, stopping all containers")
    for container in get_containers():
        container.stop()
    import sys

    sys.exit(1)


def get_free_cpu(cpu_range: set[str]) -> str | None:
    try:
        used_cpu = set()
        for container in get_containers():
            used_cpu.add(container.attrs["HostConfig"]["CpusetCpus"])
        for cpu in cpu_range:
            if cpu not in used_cpu:
                return cpu
        return None
    except NotFound:
        return None


def get_index(path: str | Path) -> int:
    path = Path(path)
    if not path.exists():
        return 1
    index = [1]
    for p in path.iterdir():
        if p.is_dir() and p.name.isdigit():
            index.append(int(p.name))
    return max(index) + 1


def fuzzing(
    work_dir: str | Path,
    fuzzers: list[str],
    targets: list[str],
    timeout: str,
    repeat: int = 1,
    *,
    cpu_range: (list[str | int] | set[str | int]) | None = None,
    script_path: str = (Path(__file__).parent.absolute() / "start.sh").as_posix(),
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
    global OWNER
    OWNER = str(datetime.datetime.now())
    # check if the images exist
    for fuzzer in fuzzers:
        for target in targets:
            target_image_name = get_target_image_name(fuzzer, target)
            assert is_image_exist(
                target_image_name
            ), f"docker image {target_image_name} not found"
    signal.signal(signal.SIGINT, sigint_handler)
    for repeat_index in range(repeat):
        for fuzzer in fuzzers:
            for target in targets:
                cpu_id = get_free_cpu(cpu_range)  # type: ignore
                while cpu_id is None:
                    time.sleep(10)
                    cpu_id = get_free_cpu(cpu_range)  # type: ignore
                base_path = work_dir / "archive" / fuzzer / target
                index = str(get_index(base_path))
                host_path = base_path / index
                host_path.mkdir(parents=True)
                container = docker.from_env().containers.run(
                    image=get_target_image_name(fuzzer, target),
                    command=f"-c 'timeout {timeout} ${{SRC}}/script.sh'",
                    remove=True,
                    cap_add=["SYS_PTRACE"],
                    cpuset_cpus=cpu_id,
                    detach=True,
                    name=f"{fuzzer}-{target}-{index}",
                    network_mode="none",
                    privileged=True,
                    tty=True,
                    security_opt=["seccomp=unconfined"],
                    environment={
                        "CPU_ID": cpu_id,
                    },
                    volumes={
                        host_path.as_posix(): {"bind": "/shared", "mode": "rw"},
                        script_path: {"bind": "/src/script.sh", "mode": "ro"},
                    },  # type: ignore
                    labels={
                        "fuzzer": fuzzer,
                        "target": target,
                        "owner": OWNER,
                    },
                )
                print(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    container.short_id,
                    fuzzer.ljust(16),
                    target.ljust(10),
                    str(repeat_index).ljust(3),
                    "starts on cpu",
                    cpu_id,
                )
    try:
        containers = get_containers()
        if containers:
            for container in containers:
                container.wait()
    except NotFound:
        pass
    except Exception as e:
        print(e)
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} DONE")
    print(f"The results can be found in {work_dir/'archive'}")
