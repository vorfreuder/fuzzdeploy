import datetime
import re

import docker


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
