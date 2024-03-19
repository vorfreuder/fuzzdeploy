import hashlib
import os
import re
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


def parse_path_by(path):
    path_parts = path.split("/")
    for i, part in enumerate(path_parts):
        if part == "ar" or part == "triage_by_casr":
            index = i
            break
    else:
        assert False, f"Can't find ar or triage_by_casr in {path}!"
    fuzzer = path_parts[index + 1]
    target = path_parts[index + 2]
    repeat = path_parts[index + 3]
    return fuzzer, target, repeat


def summary_paths(work_dir):
    tbc_path = os.path.join(work_dir, "triage_by_casr")
    assert os.path.exists(tbc_path), f"{tbc_path} not exists"
    for fuzzer in os.listdir(tbc_path):
        fuzzer_path = os.path.join(tbc_path, fuzzer)
        if not os.path.isdir(fuzzer_path):
            continue
        for target in os.listdir(fuzzer_path):
            target_path = os.path.join(fuzzer_path, target)
            if not os.path.isdir(target_path):
                continue
            for repeat in os.listdir(target_path):
                repeat_path = os.path.join(target_path, repeat)
                if not os.path.isdir(repeat_path):
                    continue
                summary_path = os.path.join(repeat_path, "summary_by_unique_line")
                assert os.path.exists(summary_path), f"{summary_path} not exists"
                yield summary_path


def search_file(dir, file_name):
    for root, dirs, files in os.walk(dir):
        if file_name in files:
            return os.path.join(root, file_name)
    return None


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
