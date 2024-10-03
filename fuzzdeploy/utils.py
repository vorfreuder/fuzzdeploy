import datetime
import hashlib
import re
from pathlib import Path
from typing import NamedTuple

import docker
from docker.models.containers import Container


def is_image_exist(image_name: str):
    client = docker.from_env()
    try:
        client.images.get(image_name)
        return True
    except:
        return False


def get_fuzzer_image_name(fuzzer: str):
    return f"{fuzzer}:fuzzdeploy"


def get_target_image_name(fuzzer: str, target: str):
    return f"{fuzzer}:{target}"


def get_past_sec(container) -> int:
    time_str = container.attrs["State"]["StartedAt"]
    time_str = time_str[: time_str.index(".")]
    dt = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    delta = now - dt
    return int(delta.total_seconds())


def time_to_seconds(time_str):
    time_units = {
        "d": 86400,
        "h": 3600,
        "m": 60,
        "s": 1,
    }
    pattern = re.compile(r"(\d+)([dhms])")
    total_seconds = 0
    for match in pattern.finditer(time_str):
        quantity = int(match.group(1))
        unit = match.group(2)
        total_seconds += quantity * time_units[unit]
    return total_seconds


class WorkDirItem(NamedTuple):
    fuzzer: str
    target: str
    idx: str
    path: Path
    sub_dir: str
    work_dir: Path


def work_dir_iterdir(work_dir: str | Path, sub_dir: str):
    work_dir = Path(work_dir).absolute()
    sub_work_dir = work_dir / sub_dir
    assert sub_work_dir.exists(), f"{sub_work_dir} not exists"
    for fuzzer in sorted(sub_work_dir.iterdir()):
        if not fuzzer.is_dir():
            continue
        for target in sorted(fuzzer.iterdir()):
            if not target.is_dir():
                continue
            for idx in sorted(target.iterdir()):
                if not idx.is_dir():
                    continue
                yield WorkDirItem(
                    fuzzer=fuzzer.name,
                    target=target.name,
                    idx=idx.name,
                    path=sub_work_dir / fuzzer / target / idx,
                    sub_dir=sub_dir,
                    work_dir=work_dir,
                )


def get_item_path(path: str | Path, item: str) -> Path | None:
    dir_ls = []
    for p in Path(path).glob("*"):
        if p.name == item:
            return p
        if p.is_dir():
            dir_ls.append(p)
    for p in dir_ls:
        for pp in p.glob("*"):
            if pp.name == item:
                return pp
    return None


def remove_exited_container(container_ls: list[Container]):
    removed_container_ls = []
    for container in container_ls:
        container.reload()
        if container.status == "exited":
            container.remove()
            removed_container_ls.append(container)
    for container in removed_container_ls:
        container_ls.remove(container)


def get_free_cpu(container_ls: list[Container], cpu_range: set[str]) -> str | None:
    used_cpu = set()
    for container in container_ls:
        container.reload()
        for cpu in container.attrs["HostConfig"]["CpusetCpus"].split(","):
            used_cpu.add(cpu)
    for cpu in cpu_range:
        if cpu not in used_cpu:
            return cpu
    return None


VULNERABILITY_SEVERITY = {
    "EXPLOITABLE": (
        "SegFaultOnPc",
        "ReturnAv",
        "BranchAv",
        "CallAv",
        "DestAv",
        "BranchAvTainted",
        "CallAvTainted",
        "DestAvTainted",
        "heap-buffer-overflow(write)",
        "global-buffer-overflow(write)",
        "stack-use-after-scope(write)",
        "stack-use-after-return(write)",
        "stack-buffer-overflow(write)",
        "stack-buffer-underflow(write)",
        "heap-use-after-free(write)",
        "container-overflow(write)",
        "param-overlap",
    ),
    "PROBABLY_EXPLOITABLE": (
        "BadInstruction",
        "SegFaultOnPcNearNull",
        "BranchAvNearNull",
        "CallAvNearNull",
        "HeapError",
        "StackGuard",
        "DestAvNearNull",
        "heap-buffer-overflow",
        "global-buffer-overflow",
        "stack-use-after-scope",
        "use-after-poison",
        "stack-use-after-return",
        "stack-buffer-overflow",
        "stack-buffer-underflow",
        "heap-use-after-free",
        "container-overflow",
        "negative-size-param",
        "calloc-overflow",
        "readllocarray-overflow",
        "pvalloc-overflow",
        "overwrites-const-input",
    ),
    "NOT_EXPLOITABLE": (
        "SourceAv",
        "AbortSignal",
        "AccessViolation",
        "SourceAvNearNull",
        "SafeFunctionCheck",
        "FPE",
        "StackOverflow",
        "double-free",
        "bad-free",
        "alloc-dealloc-mismatch",
        "heap-buffer-overflow(read)",
        "global-buffer-overflow(read)",
        "stack-use-after-scope(read)",
        "stack-use-after-return(read)",
        "stack-buffer-overflow(read)",
        "stack-buffer-underflow(read)",
        "heap-use-after-free(read)",
        "container-overflow(read)",
        "initialization-order-fiasco",
        "new-delete-type-mismatch",
        "bad-malloc_usable_size",
        "odr-violation",
        "memory-leaks",
        "invalid-allocation-alignment",
        "invalid-aligned-alloc-alignment",
        "invalid-posix-memalign-alignment",
        "allocation-size-too-big",
        "out-of-memory",
        "fuzz target exited",
        "timeout",
    ),
}


def is_heap_related_vulnerability(vul_type):
    vul_type = str(vul_type).strip()
    if "stack" in vul_type.lower():
        return False
    return vul_type not in (
        "param-overlap",
        "BadInstruction",
        "overwrites-const-input",
        "AbortSignal",
        "SafeFunctionCheck",
        "FPE",
        "initialization-order-fiasco",
        "odr-violation",
        "fuzz target exited",
        "timeout",
    )


def hash_path(path: str | Path) -> str:
    path = Path(path).absolute()
    hasher = hashlib.sha256()
    for filename in path.iterdir():
        if filename.is_dir():
            continue
        hasher.update(filename.name.encode())
    return hasher.hexdigest()
