import os
import time
from pathlib import Path
from typing import Callable

import docker
from docker.errors import APIError
from docker.models.containers import Container

from .build import build_images
from .utils import (
    WorkDirItem,
    get_free_cpu,
    get_target_image_name,
    remove_exited_container,
    work_dir_iterdir,
)


def make(
    *,
    work_dir: str | Path,
    sub_dir: str,
    base_image: str,
    skip_handler: Callable[[WorkDirItem], bool] | None = None,
    cpu_range: (list[str | int] | set[str | int]) | None = None,
    environment: dict | None = None,
) -> None:
    assert sub_dir, "sub_dir should not be None"
    assert base_image, "base_image should not be None"
    if cpu_range is not None:
        cpu_range = [str(i) for i in cpu_range]
    else:
        cpu_range = set(
            [str(i) for i in range(int(docker.from_env().info().get("NCPU")))]
        )
    assert cpu_range, "cpu_range should contain one element at least"
    if not environment:
        environment = {}
    work_dir = Path(work_dir).absolute()
    todo_ls: list[WorkDirItem] = []
    for item in work_dir_iterdir(work_dir, "archive"):
        if skip_handler and skip_handler(item):
            continue
        assert item.path.exists(), f"{item.path} not exists"
        todo_ls.append(item)
    if not todo_ls:
        return
    build_image_result_ls = build_images(
        fuzzers=[base_image],
        targets=list(set([_.target for _ in todo_ls])),
        log_path=work_dir / "logs",
    )
    for build_image_result in build_image_result_ls:
        assert (
            build_image_result.code == 0
        ), f"{build_image_result.image_name} build failed"
    container_ls: list[Container] = []
    for item in todo_ls:
        dst_path = work_dir / sub_dir / item.fuzzer / item.target / item.idx
        dst_path.mkdir(parents=True, exist_ok=True)
        cpu_id = get_free_cpu(container_ls, cpu_range)  # type: ignore
        while cpu_id is None:
            time.sleep(10)
            remove_exited_container(container_ls)
            cpu_id = get_free_cpu(container_ls, cpu_range)  # type: ignore
        container = docker.from_env().containers.run(
            image=get_target_image_name(base_image, item.target),
            command=f"-c '${{SRC}}/script.sh'",
            # command=f"-c bash",
            cap_add=["SYS_PTRACE"],
            cpuset_cpus=cpu_id,
            detach=True,
            name=f"{base_image}-{item.fuzzer}-{item.target}-{item.idx}",
            network_mode="none",
            privileged=True,
            tty=True,
            security_opt=["seccomp=unconfined"],
            environment={
                "DST": "/dst",
                **environment,
            },
            volumes={
                item.path.as_posix(): {"bind": "/shared", "mode": "rw"},
                dst_path.as_posix(): {"bind": "/dst", "mode": "rw"},
                (
                    Path(__file__).parent.parent.absolute()
                    / "fuzzers"
                    / base_image
                    / "run.sh"
                ).as_posix(): {
                    "bind": "/src/script.sh",
                    "mode": "ro",
                },
            },  # type: ignore
            labels={
                "fuzzer": item.fuzzer,
                "target": item.target,
                "idx": item.idx,
                "dst_path": dst_path.as_posix(),
            },
            user=f"{os.getuid()}:{os.getgid()}",
        )
        container_ls.append(container)
    # allocate more cpu
    while True:
        remove_exited_container(container_ls)
        if not container_ls:
            break
        cpu_id = get_free_cpu(container_ls, cpu_range)  # type: ignore
        if not cpu_id:
            time.sleep(10)
            continue
        cpu_bindings = {}
        for container in container_ls:
            container.reload()
            cpuset_cpus = container.attrs["HostConfig"]["CpusetCpus"].split(",")
            cpu_bindings[container.id] = {
                "container": container,
                "cpus": cpuset_cpus,
                "cpu_count": len(cpuset_cpus),
            }
        min_cpu_container = min(cpu_bindings.values(), key=lambda x: x["cpu_count"])
        min_cpu_container["cpus"].append(cpu_id)
        try:
            min_cpu_container["container"].update(
                cpuset_cpus=",".join(min_cpu_container["cpus"])
            )
        # in case of container not running
        except APIError:
            pass
        except:
            raise
