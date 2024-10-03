from pathlib import Path

import pandas as pd

from .make import make
from .utils import WorkDirItem, get_item_path, hash_path, work_dir_iterdir


def _skip_handler(item: WorkDirItem) -> bool:
    dst_path = item.work_dir / "aflcov" / item.fuzzer / item.target / item.idx
    hash_file = dst_path / ".hash"
    if not dst_path.exists() or not hash_file.exists():
        return False
    dst_hash = open(hash_file, "r").read()
    queue_path = get_item_path(
        item.work_dir / "archive" / item.fuzzer / item.target / item.idx, "queue"
    )
    assert queue_path, f"{queue_path} not found"
    queue_hash = hash_path(queue_path)
    if dst_hash == queue_hash:
        return True
    hash_file.unlink()
    return False


def get(work_dir: str | Path):
    work_dir = Path(work_dir).absolute()
    make(
        work_dir=work_dir,
        sub_dir="aflcov",
        base_image="aflcov",
        skip_handler=_skip_handler,
    )
    res_ls = []
    for item in work_dir_iterdir(work_dir, "aflcov"):
        log_path = item.path / "afl-cov.log"
        assert log_path.exists(), f"{log_path} not found"
        for line in open(log_path, "r").read().split("\n"):
            if line.lstrip().startswith("lines"):
                line_coverage = line.split(":", 1)[1].split("%", 1)[0].strip()
                res_ls.append(
                    {
                        "fuzzer": item.fuzzer,
                        "target": item.target,
                        "idx": item.idx,
                        "line_coverage": line_coverage,
                    }
                )
                break
        with open(item.path / ".hash", "w") as f:
            queue_path = get_item_path(
                item.work_dir / "archive" / item.fuzzer / item.target / item.idx,
                "queue",
            )
            assert queue_path, f"{queue_path} not found"
            f.write(hash_path(queue_path))
    df = pd.DataFrame(res_ls)
    return df
