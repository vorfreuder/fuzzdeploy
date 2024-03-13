import time

import psutil

from . import utility


class CpuAllocator:
    def __init__(self, CPU_RANGE=None):
        if CPU_RANGE is None:
            CPU_RANGE = [str(i) for i in range(psutil.cpu_count())]
        assert (
            len(CPU_RANGE) <= psutil.cpu_count()
            and max([int(_) for _ in CPU_RANGE]) < psutil.cpu_count()
            and min([int(_) for _ in CPU_RANGE]) >= 0
        ), f"Requested CPUs are not available - available: 0-{psutil.cpu_count() - 1}"
        self.free_cpu_ls = [str(_) for _ in CPU_RANGE]
        self.container_id_dict = {}

    @staticmethod
    def is_container_running(container_id):
        res = utility.get_cmd_res(
            f"docker inspect --format '{{{{.State.Running}}}}' {container_id} 2>/dev/null"
        )
        if res != None:
            res = res.strip()
        return res == "true"

    def recycle_cpus(self):
        for container_id in list(self.container_id_dict.keys()):
            if not CpuAllocator.is_container_running(container_id):
                self.free_cpu_ls.extend(self.container_id_dict.pop(container_id))

    def get_free_cpu(self, sleep_time=10, time_out=None):
        # Recycling idle cpus
        if time_out is not None:
            start_time = time.time()
            assert (
                time_out > 0 and time_out >= sleep_time
            ), "time_out should be positive and greater than sleep_time"
        while not self.has_free_cpu():
            self.recycle_cpus()
            time.sleep(sleep_time)
            if time_out is not None and time.time() - start_time >= time_out:
                return None
        return self.free_cpu_ls.pop(0)

    def append(self, container_id, cpu_id):
        self.container_id_dict.setdefault(container_id, []).append(cpu_id)
        return self.container_id_dict[container_id]

    def get_container_id_ls(self):
        return list(self.container_id_dict.keys())

    def get_cpu_ls_by_container_id(self, container_id):
        return self.container_id_dict.get(container_id, [])

    def has_free_cpu(self):
        return len(self.free_cpu_ls) > 0

    def wait_for_done(self):
        for container_id in self.container_id_dict.keys():
            utility.get_cmd_res(f"docker wait {container_id} 2> /dev/null")
