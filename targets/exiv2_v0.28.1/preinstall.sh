#!/bin/bash
set -e

apt-get update
apt-get install -y libexpat1-dev zlib1g-dev libbrotli-dev

cd $TARGET
if [ ! -f "cmake-3.27.6-linux-x86_64.tar.gz" ]; then
    wget https://cmake.org/files/v3.27/cmake-3.27.6-linux-x86_64.tar.gz
fi
tar -xzvf cmake-3.27.6-linux-x86_64.tar.gz
sudo ln -sf $TARGET/cmake-3.27.6-linux-x86_64/bin/* /usr/bin/
rm cmake-3.27.6-linux-x86_64.tar.gz
