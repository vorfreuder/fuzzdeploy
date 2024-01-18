import os
import re
import subprocess
import time

import psutil
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.traceback import install

install()
console = Console()


def get_free_cpu_range():
    while True:
        cpu_count = psutil.cpu_count()
        num_samples = 5
        cpu_percent_samples = [
            psutil.cpu_percent(interval=0.1, percpu=True) for _ in range(num_samples)
        ]
        avg_cpu_percent = [
            sum(cpu_percent[i] for cpu_percent in cpu_percent_samples) / num_samples
            for i in range(cpu_count)
        ]
        free_cpu_range = [i for i, load in enumerate(avg_cpu_percent) if load <= 50]
        if len(free_cpu_range) > 0:
            return free_cpu_range
        time.sleep(1)


def get_cmd_res(command):
    try:
        return subprocess.check_output(command, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        # print("Error executing command:", e)
        return None


def is_container_running(container_id):
    res = get_cmd_res(
        f"docker inspect --format '{{{{.State.Running}}}}' {container_id} 2>/dev/null"
    )
    if res != None:
        res = res.strip()
    return res == "true"


def realLength(string):
    """Calculate the byte length of a mixed single- and double-byte string"""
    dualByteNum = len("".join(re.compile("[^\x00-\xff]+").findall(string)))
    singleByteNum = len(string) - dualByteNum
    return (dualByteNum, singleByteNum, dualByteNum * 2 + singleByteNum)


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
    if "ar" in path_parts:
        ar_index = path_parts.index("ar")
    elif "triage_by_casr" in path_parts:
        ar_index = path_parts.index("triage_by_casr")
    else:
        assert False, f"Can't find ar or triage_by_casr in {path}!"
    fuzzer = path_parts[ar_index + 1]
    target = path_parts[ar_index + 2]
    repeat = path_parts[ar_index + 3]
    return fuzzer, target, repeat


def test_paths(work_dir):
    ar_path = os.path.join(work_dir, "ar")
    for fuzzer in os.listdir(ar_path):
        fuzzer_path = os.path.join(ar_path, fuzzer)
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
                yield repeat_path


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
