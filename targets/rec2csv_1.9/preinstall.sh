#!/bin/bash
set -e

apt-get update
apt-get install -y autoconf pkg-config help2man

cd $TARGET
if [ ! -f "automake-1.16.5.tar.gz" ]; then
    wget https://ftp.gnu.org/gnu/automake/automake-1.16.5.tar.gz
fi
tar -xvf automake-1.16.5.tar.gz
cd automake-1.16.5
./configure
make
make install
cd ..
rm -rf automake-1.16.5
rm automake-1.16.5.tar.gz
