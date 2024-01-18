#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
    sudo tmux htop git wget \
    make build-essential gcc-7-plugin-dev gnupg \
    lsb-release software-properties-common \
    cmake

cd "$FUZZER"

if [ ! -f "llvm-6.0.0.src.tar.xz" ]; then
    wget https://releases.llvm.org/6.0.0/llvm-6.0.0.src.tar.xz
fi
if [ ! -f "cfe-6.0.0.src.tar.xz" ]; then
    wget https://releases.llvm.org/6.0.0/cfe-6.0.0.src.tar.xz
fi
if [ ! -f "compiler-rt-6.0.0.src.tar.xz" ]; then
    wget https://releases.llvm.org/6.0.0/compiler-rt-6.0.0.src.tar.xz
fi
tar -xvf llvm-6.0.0.src.tar.xz
mv llvm-6.0.0.src llvm
tar -xvf cfe-6.0.0.src.tar.xz
mv cfe-6.0.0.src llvm/tools/clang
tar -xvf compiler-rt-6.0.0.src.tar.xz
mv compiler-rt-6.0.0.src compiler-rt
mkdir build
cd build
cmake -G "Unix Makefiles" -DLLVM_ENABLE_ASSERTIONS=On -DCMAKE_BUILD_TYPE=Release ../llvm
make -j $(nproc)
make install
cd ..
mkdir build2
cd build2
cmake -G "Unix Makefiles" -DLLVM_ENABLE_ASSERTIONS=On -DCMAKE_BUILD_TYPE=Release ../compiler-rt
make -j $(nproc)
mkdir -p /usr/local/lib/clang/6.0.0/lib/
mv "$FUZZER"/build2/lib/linux /usr/local/lib/clang/6.0.0/lib/linux

cd ..
rm llvm-6.0.0.src.tar.xz cfe-6.0.0.src.tar.xz compiler-rt-6.0.0.src.tar.xz
rm -rf llvm compiler-rt build build2
