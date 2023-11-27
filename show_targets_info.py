import os

from prettytable import PrettyTable

TARGETS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "targets")
res = []
for target in os.listdir(TARGETS_DIR):
    fetch_path = os.path.join(TARGETS_DIR, target, "fetch.sh")
    assert os.path.exists(fetch_path), f"fetch.sh not found in {fetch_path}"
    tmp = [target]
    with open(fetch_path, "r") as f:
        for line in f:
            if line.startswith("# Date:"):
                tmp.append(line.lstrip("# Date:").strip())
            elif line.startswith("# Version:"):
                tmp.append(line.lstrip("# Version:").strip())
    res.append(tmp)
res.sort(key=lambda x: x[0])
prettytable = PrettyTable()
prettytable.align = "l"
prettytable.field_names = ["target", "date", "version"]
prettytable.sortby = "target"
prettytable.add_rows(res)
print(prettytable)
