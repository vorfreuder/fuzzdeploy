#!/usr/bin/python3

import json
import multiprocessing
import os
import subprocess


def get_cmd_res(command):
    try:
        return subprocess.check_output(command, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return None


SHARED = os.environ.get("SHARED")
AFLSHOWMAP = os.environ.get("AFLSHOWMAP")
OUT = os.environ.get("OUT")

edges_path = os.path.join(AFLSHOWMAP, "edges")

target_args = OUT + "/" + open(os.path.join(SHARED, "target_args")).readline().strip()
# may not need?
if "@@" not in target_args:
    target_args = target_args + " < @@"
queue_path = None
for root, dirs, files in os.walk(SHARED):
    if "queue" in dirs:
        queue_path = os.path.join(root, "queue")
        break
if queue_path is None:
    print("Error: queue folder not found")
    exit(1)

queue_path_files = set(
    [_ for _ in os.listdir(queue_path) if os.path.isfile(os.path.join(queue_path, _))]
)
edges_path_files = set(os.listdir(edges_path))
diff_set = queue_path_files.difference(edges_path_files)
with multiprocessing.Pool() as pool:
    results = pool.imap_unordered(
        get_cmd_res,
        [
            f"$FUZZER/repo/afl-showmap -t 3000 -o {os.path.join(edges_path,file)} -q -- {target_args.replace('@@', os.path.join(queue_path, file))}"
            for file in diff_set
        ],
    )
    for result in results:
        pass
# rocord edges over seeds
edges_over_seeds = {}
unique_edges = set()
for edge_file in sorted(os.listdir(edges_path)):
    if not edge_file.startswith("id:"):
        continue
    with open(
        os.path.join(
            edges_path,
            edge_file,
        ),
        "r",
    ) as file:
        for line in file:
            unique_edges.add(line.split(":")[0].strip())
    edges_over_seeds[int(edge_file.split(",")[0].lstrip("id:")) + 1] = len(unique_edges)
with open(os.path.join(AFLSHOWMAP, "edges_over_seeds.log"), "w", encoding="utf-8") as f:
    json.dump(edges_over_seeds, f, ensure_ascii=False, indent=4)
