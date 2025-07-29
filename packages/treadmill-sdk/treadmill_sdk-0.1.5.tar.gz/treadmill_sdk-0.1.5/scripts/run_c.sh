#!/bin/bash
set -e

# colorful echo functions
function echo_y() { echo -e "\033[1;33m$@\033[0m"; } # yellow
function echo_r() { echo -e "\033[0;31m$@\033[0m"; } # red

# 获取脚本所在目录
SCRIPT_DIR="$(dirname $0)"

# 切换到脚本所在目录（如果当前目录不是脚本所在目录）
[ "$(pwd)" != "$SCRIPT_DIR" ] && cd "$SCRIPT_DIR"
echo_y "current dir: $(pwd)"

cd ..

cd examples/c/mac/
make
make run
