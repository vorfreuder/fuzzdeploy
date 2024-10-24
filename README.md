<h3>

```
    ___                           _                _
   / __)                         | |              | |
  | |__  _   _  _____  _____   _ | |  ____  ____  | |  ___   _   _
  |  __)| | | |(___  )(___  ) / || | / _  )|  _ \ | | / _ \ | | | |
  | |   | |_| | / __/  / __/ ( (_| |( (/ / | | | || || |_| || |_| |
  |_|    \____|(_____)(_____) \____| \____)| ||_/ |_| \___/  \__  |
                                           |_|              (____/
```
</h3>
<div align="center">

![Static Badge](https://img.shields.io/badge/AFL%2FAFL%2B%2B-%2300A98F?style=for-the-badge&logo=vowpalwabbit&logoColor=%23FF9A00&label=fuzzers%20based)

![OS](https://img.shields.io/badge/OS-Linux-%23FCC624?style=for-the-badge&logo=linux)
![GitHub repo size](https://img.shields.io/github/repo-size/Eterniter/fuzzdeploy?style=for-the-badge&logo=republicofgamers)
![License](https://img.shields.io/github/license/Eterniter/fuzzdeploy?style=for-the-badge&logo=scpfoundation)

___Python3 scripts for [AFL](https://lcamtuf.coredump.cx/afl/)/[AFL++](https://github.com/AFLplusplus/AFLplusplus) based fuzzers to deploy fuzzing with docker / monitor / triage.___
</div>
<p align="center">
  <a href="#introduction">Introduction</a> •
  <a href="#prerequisite">Prerequisite</a> •
  <a href="#organization">Organization</a> •
  <a href="#usage">Usage</a>
</p>

## Introduction
Inspired by [MAGMA](https://hexhive.epfl.ch/magma/), fuzzdeploy is a collection of Python3 scripts for [AFL](https://lcamtuf.coredump.cx/afl/)/[AFL++](https://github.com/AFLplusplus/AFLplusplus) based fuzzers to deploy fuzzing with [docker](https://www.docker.com), monitor the status of fuzzers and triage crash based on the unique line of [casr](https://github.com/ispras/casr).

## Prerequisite
```bash
#!/bin/bash
set -e
apt-get update
apt-get install -y sudo tmux htop git curl python3 python3-pip python3-venv rsync
curl -sS https://webinstall.dev/shfmt | bash
# install python3 packages
# export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
pip3 install openpyxl black isort numpy pandas styleframe docker
# install docker if you need
sudo apt-get update \
    && sudo apt-get install -y ca-certificates curl gnupg \
    && sudo install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && sudo chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && sudo apt-get update \
    && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# sudo usermod -aG docker $USER
echo core | sudo tee /proc/sys/kernel/core_pattern
sudo bash -c 'cd /sys/devices/system/cpu; echo performance | tee cpu*/cpufreq/scaling_governor'
```
Python 3.10.12 and Ubuntu 22.04.5 LTS work fine.

## Organization
`Note that the target should be compiled with address sanitizer successfully so as to be triaged by casr.`

Place fuzzer in [fuzzers](/fuzzers) and target in [targets](/targets) with some scripts like those examples does.

### Fuzzer Configuration
| File | Description |
| --- | --- |
| preinstall.sh | Installs the fuzzer's dependencies. |
| fetch.sh | Retrieves the fuzzer's source code. Typically stores it in $FUZZER/repo. |
| build.sh | Builds the fuzzer. |
| instrument.sh | Compiles the target, performing any required pre-processing. |
| run.sh | Runs the fuzzer. |

### Target Configuration
| File | Description |
| --- | --- |
| preinstall.sh | Installs the target's dependencies. |
| fetch.sh | Retrieves the target's source code. Typically stores it in $TARGET/repo. |
| build.sh | Compiles the target and copy it to $PROGRAM. |
| corpus | Seeds given to the fuzzer as input. |
| target_args | Command line of the target given to the fuzzer to execute. |

## Usage
```python
from pathlib import Path
import fuzzdeploy

fuzzers = [
    "afl",
]
targets = [
    "mjs_latest",
    "yasm_latest",
]
work_dir = Path("./workdir_tmp2")
retry = 3
while retry > 0:
    retry -= 1
    # build images
    fuzzdeploy.build_images(
        fuzzers=fuzzers,
        targets=targets,
        log_path=work_dir / "logs",
        # skip_existed_fuzzer_images=False,
        # skip_existed_target_images=False,
    )

# start fuzzing
fuzzdeploy.fuzzing(
    work_dir=work_dir,
    fuzzers=fuzzers,
    targets=targets,
    timeout="1h",
    repeat=2,
)

fuzzdeploy.fuzzer_state.to_excel(work_dir)

fuzzdeploy.casr.to_excel(work_dir)
```

For more information, just resort to [source code](https://github.com/vorfreuder/fuzzdeploy).
