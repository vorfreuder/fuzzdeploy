import multiprocessing
import os
import shutil
import tempfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import NamedTuple

import docker

from .utils import get_fuzzer_image_name, get_target_image_name, is_image_exist


class BuildStatus(Enum):
    FUZZER_BUILD_FAILURE = "fuzzer build failure"
    TARGET_BUILD_FAILURE = "target build failure"
    FUZZER_IMAGE_EXISTENCE = "fuzzer image existence"
    FUZZER_IMAGE_NOT_EXISTENCE = "fuzzer image not existence"
    TARGET_IMAGE_EXISTENCE = "target image existence"
    TARGET_IMAGE_NOT_EXISTENCE = "target image not existence"
    FUZZER_BUILD_SUCCESS = "fuzzer build success"
    TARGET_BUILD_SUCCESS = "target build success"


TOP_DIR = Path(__file__).resolve().parent.parent
NOW = datetime.now().strftime("%Y%m%d%H%M")


class BuildImageResult(NamedTuple):
    image_name: str
    fuzzer: str
    target: str | None
    code: int
    status: BuildStatus
    log_path: str | None


def remove_image(image_name: str):
    client = docker.from_env()
    try:
        client.images.remove(image_name, force=True)
    except:
        pass


def write_log(logs, log_path: str | Path):
    is_error = False
    log_path = Path(log_path)
    with open(log_path, "w") as f:
        for log in logs:
            try:
                if log.get("stream"):
                    f.write(log["stream"])
                elif log.get("error"):
                    f.write(log["error"])
                    is_error = True
            except FileNotFoundError:
                pass
    status = "success" if not is_error else "error"
    if log_path.exists():
        log_path = log_path.rename(
            log_path.with_name(f"{NOW}-{status}-{log_path.name}")
        )
    return log_path, is_error


def build_fuzzer(
    fuzzer: str, log_path: str | Path, *, skip_existed_images: bool = True
) -> BuildImageResult:
    fuzzer_image = get_fuzzer_image_name(fuzzer)
    if is_image_exist(fuzzer_image):
        if skip_existed_images:
            return BuildImageResult(
                image_name=fuzzer_image,
                fuzzer=fuzzer,
                target=None,
                code=0,
                status=BuildStatus.FUZZER_IMAGE_EXISTENCE,
                log_path=None,
            )
        else:
            remove_image(fuzzer_image)
    log_path = Path(log_path).absolute()
    log_path.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{fuzzer}-") as ctx_path:
        ctx_path = Path(ctx_path)
        shutil.copytree(
            TOP_DIR / "fuzzers" / fuzzer, ctx_path / "fuzzer", symlinks=True
        )
        logs = docker.from_env().api.build(
            path=ctx_path.as_posix(),
            dockerfile=(TOP_DIR / "fuzzdeploy" / "Dockerfile_fuzzer").as_posix(),
            tag=fuzzer_image,
            buildargs={
                "fuzzer_name": fuzzer,
                "USER_ID": str(os.getuid()),
                "GROUP_ID": str(os.getgid()),
            },
            rm=True,
            decode=True,
        )
        fuzzer_log_path = log_path / f"{fuzzer}.log"
        fuzzer_log_path, is_error = write_log(logs, fuzzer_log_path)
        tmp_com_args = {
            "image_name": fuzzer_image,
            "fuzzer": fuzzer,
            "target": None,
            "log_path": fuzzer_log_path.as_posix(),
        }
        if is_error:
            return BuildImageResult(
                **tmp_com_args,
                code=1,
                status=BuildStatus.FUZZER_BUILD_FAILURE,
            )
    return BuildImageResult(
        **tmp_com_args,
        code=0,
        status=BuildStatus.FUZZER_BUILD_SUCCESS,
    )


def build_target(
    fuzzer: str, target: str, log_path: str | Path, *, skip_existed_images: bool = True
) -> BuildImageResult:
    image = get_target_image_name(fuzzer, target)
    tmp_com_args = {
        "image_name": image,
        "fuzzer": fuzzer,
        "target": target,
        "log_path": None,
    }
    if is_image_exist(image):
        if skip_existed_images:
            return BuildImageResult(
                **tmp_com_args,
                code=0,
                status=BuildStatus.TARGET_IMAGE_EXISTENCE,
            )
        else:
            remove_image(image)
    log_path = Path(log_path).absolute()
    log_path.mkdir(parents=True, exist_ok=True)
    if not is_image_exist(get_fuzzer_image_name(fuzzer)):
        return BuildImageResult(
            **tmp_com_args,
            code=1,
            status=BuildStatus.FUZZER_IMAGE_NOT_EXISTENCE,
        )
    with tempfile.TemporaryDirectory(prefix=f"{fuzzer}-{target}-") as ctx_dir:
        ctx_dir = Path(ctx_dir)
        shutil.copytree(TOP_DIR / "targets" / target, ctx_dir / "target", symlinks=True)
        logs = docker.from_env().api.build(
            path=ctx_dir.as_posix(),
            dockerfile=(TOP_DIR / "fuzzdeploy" / "Dockerfile_target").as_posix(),
            tag=image,
            buildargs={
                "fuzzer_name": fuzzer,
                "target_name": target,
            },
            rm=True,
            decode=True,
        )
        target_log_path = log_path / f"{fuzzer}_{target}.log"
        target_log_path, is_error = write_log(logs, target_log_path)
        tmp_com_args["log_path"] = target_log_path.as_posix()
        if is_error:
            return BuildImageResult(
                **tmp_com_args,
                code=1,
                status=BuildStatus.TARGET_BUILD_FAILURE,
            )
    return BuildImageResult(
        **tmp_com_args,
        code=0,
        status=BuildStatus.TARGET_BUILD_SUCCESS,
    )


def wrapper_build_fuzzer(args):
    fuzzer, log_path, skip_existed_images = args
    return build_fuzzer(
        fuzzer=fuzzer, log_path=log_path, skip_existed_images=skip_existed_images
    )


def wrapper_build_target(args):
    fuzzer, target, log_path, skip_existed_images = args
    return build_target(
        fuzzer=fuzzer,
        target=target,
        log_path=log_path,
        skip_existed_images=skip_existed_images,
    )


def build_image(
    fuzzer: str, target: str, log_path: str | Path, skip_existed_images: bool = True
) -> BuildImageResult:
    res = build_fuzzer(
        fuzzer=fuzzer,
        log_path=log_path,
        skip_existed_images=skip_existed_images,
    )
    if res.code == 1:
        return res
    return build_target(
        fuzzer=fuzzer,
        target=target,
        log_path=log_path,
        skip_existed_images=skip_existed_images,
    )


def build_images(
    fuzzers: list[str],
    targets: list[str],
    log_path: str | Path,
    *,
    skip_existed_fuzzer_images: bool = True,
    skip_existed_target_images: bool = True,
) -> list[BuildImageResult]:
    assert isinstance(fuzzers, list), "fuzzers should be a list"
    assert len(fuzzers) > 0, "fuzzers should contain one element at least"
    assert isinstance(targets, list), "targets should be a list"
    assert len(targets) > 0, "targets should contain one element at least"
    # build fuzzer images first for docker build cache
    with multiprocessing.Pool() as pool:
        results = pool.imap_unordered(
            wrapper_build_fuzzer,
            [(fuzzer, log_path, skip_existed_fuzzer_images) for fuzzer in fuzzers],
        )
        for _ in results:
            pass
    with multiprocessing.Pool() as pool:
        results = pool.imap_unordered(
            wrapper_build_target,
            [
                (fuzzer, target, log_path, skip_existed_target_images)
                for fuzzer in fuzzers
                for target in targets
            ],
        )
        return list(results)
