import hashlib
import os
import re
import shutil
import subprocess
import time
from datetime import timedelta

from rich.console import Console
from rich.traceback import install

install()
console = Console()


def get_cmd_res(command):
    try:
        return subprocess.check_output(command, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        # print("Error executing command:", e)
        return None


def time_count(msg):
    """Decorator to count the time of a function execution."""

    def timer_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            seconds = end_time - start_time

            days = seconds // (24 * 60 * 60)
            seconds %= 24 * 60 * 60
            hours = seconds // (60 * 60)
            seconds %= 60 * 60
            minutes = seconds // 60
            seconds %= 60
            elapsed_time = ""
            if days > 0:
                elapsed_time += f"{days} days, "
            if hours > 0:
                elapsed_time += f"{hours} hours, "
            if minutes > 0:
                elapsed_time += f"{minutes} minutes, "
            elapsed_time += f"{seconds:.2f} seconds"

            console.print(
                f"[bold green]\[♠][/bold green] [bold]{func.__name__} [yellow]{elapsed_time}[/yellow] {msg}[/bold]"
            )
            return result

        return wrapper

    return timer_decorator


def search_folder(dir, folder_name):
    for root, dirs, files in os.walk(dir):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None


def search_item(dir, item_type: "FILE | FOLDER", item_name):
    for root, dirs, files in os.walk(dir):
        if (item_type == "FILE" and item_name in files) or (
            item_type == "FOLDER" and item_name in dirs
        ):
            return os.path.join(root, item_name)
    return None


def get_readable_time(seconds):
    days = seconds // (24 * 60 * 60)
    seconds %= 24 * 60 * 60
    hours = seconds // (60 * 60)
    seconds %= 60 * 60
    minutes = seconds // 60
    seconds %= 60
    elapsed_time = ""
    if days > 0:
        elapsed_time += f"{days}d"
    if hours > 0:
        elapsed_time += f"{hours}h"
    if minutes > 0:
        elapsed_time += f"{minutes}m"
    elapsed_time += f"{seconds}s"
    return elapsed_time


def human_readable_to_timedelta(human_readable_time):
    matches = re.findall(r"(\d+)([dhms])", human_readable_time)

    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == "d":
            total_seconds += value * 24 * 3600
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "s":
            total_seconds += value

    return timedelta(seconds=total_seconds)


def get_workdir_paths_by(
    work_dir, suffix="ar", exclude_fuzzers=None, exclude_targets=None
):
    if not isinstance(work_dir, str):
        assert callable(work_dir), "work_dir should be a string or a callable"
        return work_dir()

    def generator():
        suffix_path = os.path.join(work_dir, suffix)
        for fuzzer in os.listdir(suffix_path):
            if exclude_fuzzers and fuzzer in exclude_fuzzers:
                continue
            fuzzer_path = os.path.join(suffix_path, fuzzer)
            if not os.path.isdir(fuzzer_path):
                continue
            for target in os.listdir(fuzzer_path):
                if exclude_targets and target in exclude_targets:
                    continue
                target_path = os.path.join(fuzzer_path, target)
                if not os.path.isdir(target_path):
                    continue
                for repeat in os.listdir(target_path):
                    repeat_path = os.path.join(target_path, repeat)
                    if not os.path.isdir(repeat_path):
                        continue
                    yield work_dir, fuzzer, target, repeat, repeat_path

    return generator()


def hash_filenames(directory):
    hasher = hashlib.sha256()
    for filename in os.listdir(directory):
        hasher.update(filename.encode())
    return hasher.hexdigest()


def remove_empty_dirs(root_dir, max_depth=5, current_depth=1):
    if current_depth > max_depth:
        return

    for entry in os.scandir(root_dir):
        if entry.is_dir():
            remove_empty_dirs(entry.path, max_depth, current_depth + 1)

    if not os.listdir(root_dir):
        os.rmdir(root_dir)


def workdir_merge(work_dir, output_dir, include_fuzzers=None, include_targets=None):
    assert output_dir is not None, "output_dir should not be None"
    assert os.path.exists(work_dir), f"{work_dir} does not exist"
    assert work_dir != output_dir, f"work_dir and output_dir should not be the same"
    fuzzers = set()
    targets = set()
    for _, fuzzer, target, _, _ in get_workdir_paths_by(work_dir):
        fuzzers.add(fuzzer)
        targets.add(target)
    if include_fuzzers:
        fuzzers = set(include_fuzzers)
    if include_targets:
        targets = set(include_targets)
    fuzzers = sorted(list(fuzzers))
    targets = sorted(list(targets))
    suffixes = [
        item
        for item in os.listdir(work_dir)
        if os.path.isdir(os.path.join(work_dir, item))
    ]
    # print(suffixes, fuzzers, targets)
    for _, fuzzer, target, repeat, _ in get_workdir_paths_by(work_dir):
        if fuzzer not in fuzzers or target not in targets:
            continue
        ar_dst = os.path.join(output_dir, "ar", fuzzer, target)
        os.makedirs(ar_dst, exist_ok=True)
        repeats = [
            int(item)
            for item in os.listdir(ar_dst)
            if os.path.isdir(os.path.join(ar_dst, item))
        ]
        repeat_dst = str(max(repeats) + 1) if repeats else "1"
        for suffix in suffixes:
            dst = os.path.join(output_dir, suffix, fuzzer, target, repeat_dst)
            assert not os.path.exists(dst), f"{dst} already exists"
        for suffix in suffixes:
            src = os.path.join(work_dir, suffix, fuzzer, target, repeat)
            if not os.path.exists(src):
                continue
            dst = os.path.join(output_dir, suffix, fuzzer, target, repeat_dst)
            os.makedirs(dst, exist_ok=True)
            for item in os.listdir(src):
                source_item = os.path.join(src, item)
                target_item = os.path.join(dst, item)
                shutil.move(source_item, target_item)
    remove_empty_dirs(work_dir)
