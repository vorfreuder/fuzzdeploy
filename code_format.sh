#!/bin/bash
set -e

cd "$(dirname "$0")"
if ! which shfmt >/dev/null 2>&1; then
    curl -sS https://webinstall.dev/shfmt | bash
fi
if ! which black >/dev/null 2>&1; then
    pip3 install black
fi
if ! which isort >/dev/null 2>&1; then
    pip3 install isort
fi
find . -maxdepth 3 -type f -name '*.sh' -exec shfmt -i 4 -w {} +
find . -maxdepth 3 -type f -name '*.py' -exec isort {} +
find . -maxdepth 3 -type f -name '*.py' -exec black {} +
