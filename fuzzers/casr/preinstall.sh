#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
    sudo tmux htop git wget \
    make build-essential gcc-7-plugin-dev gnupg \
    lsb-release software-properties-common

wget https://mirrors.tuna.tsinghua.edu.cn/llvm-apt/llvm.sh
chmod +x llvm.sh
./llvm.sh 12 all -m https://mirrors.tuna.tsinghua.edu.cn/llvm-apt
rm -f llvm.sh

apt-get install -y libc++-12-dev libc++abi-12-dev
apt-get clean -y

update-alternatives \
    --install /usr/lib/llvm llvm /usr/lib/llvm-12 20 \
    --slave /usr/bin/llvm-config llvm-config /usr/bin/llvm-config-12 \
    --slave /usr/bin/llvm-ar llvm-ar /usr/bin/llvm-ar-12 \
    --slave /usr/bin/llvm-as llvm-as /usr/bin/llvm-as-12 \
    --slave /usr/bin/llvm-bcanalyzer llvm-bcanalyzer /usr/bin/llvm-bcanalyzer-12 \
    --slave /usr/bin/llvm-c-test llvm-c-test /usr/bin/llvm-c-test-12 \
    --slave /usr/bin/llvm-cov llvm-cov /usr/bin/llvm-cov-12 \
    --slave /usr/bin/llvm-diff llvm-diff /usr/bin/llvm-diff-12 \
    --slave /usr/bin/llvm-dis llvm-dis /usr/bin/llvm-dis-12 \
    --slave /usr/bin/llvm-dwarfdump llvm-dwarfdump /usr/bin/llvm-dwarfdump-12 \
    --slave /usr/bin/llvm-extract llvm-extract /usr/bin/llvm-extract-12 \
    --slave /usr/bin/llvm-link llvm-link /usr/bin/llvm-link-12 \
    --slave /usr/bin/llvm-mc llvm-mc /usr/bin/llvm-mc-12 \
    --slave /usr/bin/llvm-nm llvm-nm /usr/bin/llvm-nm-12 \
    --slave /usr/bin/llvm-objdump llvm-objdump /usr/bin/llvm-objdump-12 \
    --slave /usr/bin/llvm-ranlib llvm-ranlib /usr/bin/llvm-ranlib-12 \
    --slave /usr/bin/llvm-readobj llvm-readobj /usr/bin/llvm-readobj-12 \
    --slave /usr/bin/llvm-rtdyld llvm-rtdyld /usr/bin/llvm-rtdyld-12 \
    --slave /usr/bin/llvm-size llvm-size /usr/bin/llvm-size-12 \
    --slave /usr/bin/llvm-stress llvm-stress /usr/bin/llvm-stress-12 \
    --slave /usr/bin/llvm-symbolizer llvm-symbolizer /usr/bin/llvm-symbolizer-12 \
    --slave /usr/bin/llvm-tblgen llvm-tblgen /usr/bin/llvm-tblgen-12 \
    --slave /usr/bin/llvm-profdata llvm-profdata /usr/bin/llvm-profdata-12

update-alternatives \
    --install /usr/bin/clang clang /usr/bin/clang-12 20 \
    --slave /usr/bin/clang++ clang++ /usr/bin/clang++-12 \
    --slave /usr/bin/clang-cpp clang-cpp /usr/bin/clang-cpp-12

export PATH=$PATH:${SRC}/cargo/bin
export CARGO_HOME=${SRC}/cargo
# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |
#     RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup \
#         sh -s -- -y
curl --proto '=https' --tlsv1.2 -sSf https://rsproxy.cn/rustup-init.sh |
    RUSTUP_DIST_SERVER=https://rsproxy.cn RUSTUP_UPDATE_ROOT=https://rsproxy.cn/rustup \
        sh -s -- -y
mkdir -vp ${CARGO_HOME:-$HOME/.cargo}
# echo -e \
#     "[source.crates-io]\nreplace-with = 'ustc'\n\n[source.ustc]\nregistry = 'git://mirrors.ustc.edu.cn/crates.io-index'" \
#     >>${CARGO_HOME:-$HOME/.cargo}/config
echo -e \
    "[source.crates-io]\nreplace-with = 'rsproxy-sparse'\n[source.rsproxy]\nregistry = 'https://rsproxy.cn/crates.io-index'\n[source.rsproxy-sparse]\nregistry = 'sparse+https://rsproxy.cn/index/'\n[registries.rsproxy]\nindex = 'https://rsproxy.cn/crates.io-index'\n[net]\ngit-fetch-with-cli = true" \
    >>${CARGO_HOME:-$HOME/.cargo}/config
cargo install casr
