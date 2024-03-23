#!/bin/bash
# Date: 2021/12/30
# Version: 1.7 latest version

set -e

if [ -d "$TARGET/repo" ]; then
    exit 0
fi

cd "$TARGET"
wget https://ftp.gnu.org/gnu/cflow/cflow-1.7.tar.gz # 2021/12/30
tar -xzf cflow-1.7.tar.gz
rm cflow-1.7.tar.gz
mv cflow-1.7 repo
