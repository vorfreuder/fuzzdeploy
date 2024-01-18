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
apt-get install -y sudo tmux htop git curl python3 python3-pip python3-venv
curl -sS https://webinstall.dev/shfmt | bash
# install python3 packages
pip3 install psutil rich openpyxl black isort
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
```

## Organization
Place fuzzer in [fuzzers](/fuzzers) and target in [targets](/targets) with some scripts like those examples does.

`Note that the target should be compiled with address sanitizer so as to be triaged by casr, and you should ensure that it is compiled successfully.`

## Usage
You may use it in this order.  
See [build_and_start.py](/build_and_start.py) to build docker images and deploy fuzzing, recommended to run it in [tmux](https://github.com/tmux/tmux).  
See [fuzzer_stats_collect.py](/fuzzer_stats_collect.py) to collect fuzzer_stats of fuzzers in workdir.  
See [triage_by_casr.py](/triage_by_casr.py) to triage crashes in workdir.  
See [joint_res.py](/joint_res.py) to combine fuzzer_stats with its triaged results.

For more information, just resort to [source code](https://github.com/Eterniter/fuzzdeploy).
