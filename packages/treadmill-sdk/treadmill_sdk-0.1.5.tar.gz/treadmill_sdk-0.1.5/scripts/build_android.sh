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

OUTPUT_LIBS_DIR=./dist/jniLibs

# cargo install cargo-ndk
cargo ndk -t arm64-v8a -t armeabi-v7a -t x86_64 -o $OUTPUT_LIBS_DIR build --release --no-default-features --features "treadmill-cbindgen"
# cargo build --release --target aarch64-linux-android  # 64位 ARM
# cargo build --release --target armv7-linux-androideabi  # 32位 ARM
# cargo build --release --target x86_64-linux-android  # x86_64
# cargo build --release --target i686-linux-android  # x86

DST_DIR=../android/treadmilljna/src/main/jniLibs/
mkdir -p $DST_DIR
cp -rfv $OUTPUT_LIBS_DIR/* $DST_DIR
