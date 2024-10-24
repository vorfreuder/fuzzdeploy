#!/bin/bash
set -e

apt-get update
apt-get install -y m4 bison autoconf automake libtool autopoint gettext help2man texinfo indent flex
