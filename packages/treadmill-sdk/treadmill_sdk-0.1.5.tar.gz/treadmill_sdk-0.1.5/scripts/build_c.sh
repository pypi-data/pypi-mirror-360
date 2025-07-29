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

if [ -n "$GITHUB_ACTIONS" ]; then
    cargo fmt
fi

cargo b --release --no-default-features --features "treadmill-cbindgen"
if [ -n "$GITHUB_ACTIONS" ]; then
    cargo fmt
fi

ZIP_NAME=mac.zip
[ -f "$ZIP_NAME" ] && rm -f "$ZIP_NAME"

# 根据操作系统设置库文件路径
OS_TYPE=$(uname -s)
case "$OS_TYPE" in
Darwin)
    DYLIB_PATH=./target/release/libtreadmill_sdk.dylib
    ZIP_NAME=mac.zip
    DEST_DIRS=(
        dist/shared/mac
    )
    ;;
Linux)
    DYLIB_PATH=./target/release/libtreadmill_sdk.so
    ZIP_NAME=linux.zip
    DEST_DIRS=(
        dist/shared/linux
    )
    ;;
MINGW* | MSYS* | CYGWIN* | Windows_NT)
    DYLIB_PATH=./target/release/treadmill_sdk.dll
    ZIP_NAME=win.zip
    DEST_DIRS=(
        dist/shared/win
    )
    ;;
*)
    echo "Unsupported OS: $OS_TYPE"
    exit 1
    ;;
esac

# 检查库文件是否存在
if [ ! -f "$DYLIB_PATH" ]; then
    echo "Library not found: $DYLIB_PATH"
    exit 1
fi

# 在 GitHub Actions 中检查 modbus（仅 macOS）
[ "$OS_TYPE" = "Darwin" ] && [ -n "$GITHUB_ACTIONS" ] && otool -tV "$DYLIB_PATH" | grep modbus

# 创建目录并复制文件
for dir in "${DEST_DIRS[@]}"; do
    mkdir -p "$dir"
    cp -fv "$DYLIB_PATH" "$dir/"
done

# UPLOAD_LIBS=FALSE
# rm -rf dist

# 在 GitHub Actions 中上传 SDK
if [ -n "$GITHUB_ACTIONS" ] || [ -n "$UPLOAD_LIBS" ]; then
    rm -rf dist/ios
    rm -rf dist/jniLibs
    zip -rv $ZIP_NAME dist
    ./scripts/upload-sdk.sh $ZIP_NAME
    exit 0
else
    cp -fv $(pwd)/dist/shared/mac/*.dylib ../android/treadmilljna/lib/macos/aarch64/
    cp -fv $(pwd)/dist/shared/linux/*.so ../android/treadmilljna/lib/linux/x86_64/

    if [ "$OS_TYPE" = "Linux" ]; then
        exit 0
    fi

    # generate C header file
    cbindgen --config cbindgen/cbindgen_treadmill.toml src/encrypt/mod.rs --output dist/include/treadmill-sdk.h --quiet

    EXAMPLE_DIR=examples/c/
    ln -sfv "$(pwd)/dist/include" $EXAMPLE_DIR
    ln -sfv "$(pwd)/dist/shared" $EXAMPLE_DIR
fi
