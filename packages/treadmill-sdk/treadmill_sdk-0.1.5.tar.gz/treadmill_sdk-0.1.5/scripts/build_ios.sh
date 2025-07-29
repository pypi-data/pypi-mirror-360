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

# 构建
IPHONEOS_DEPLOYMENT_TARGET=12.0
cargo b --release --no-default-features --features "treadmill-cbindgen" --target aarch64-apple-ios
cargo b --release --no-default-features --features "treadmill-cbindgen" --target aarch64-apple-ios-sim
cargo b --release --no-default-features --features "treadmill-cbindgen" --target x86_64-apple-ios

# 构建 iOS xcframework
LIB_NAME=treadmill_sdk

SIM_LIB=target/universal-apple-ios-sim/release/lib$LIB_NAME.a
mkdir -p target/universal-apple-ios-sim/release
lipo -create -output $SIM_LIB \
  target/aarch64-apple-ios-sim/release/lib$LIB_NAME.a \
  target/x86_64-apple-ios/release/lib$LIB_NAME.a

# otool -l target/x86_64-apple-ios/release/lib$LIB_NAME.a | grep -A 5 LC_VERSION_MIN_IPHONEOS

DST_DIR=./dist/ios
mkdir -p $DST_DIR
rm -rf $DST_DIR/$LIB_NAME.xcframework

HEADER_DIR=ios/include
rm -rf $HEADER_DIR
mkdir -p $HEADER_DIR
cp -f dist/include/treadmill-sdk.h $HEADER_DIR/
cp -f dist/include/treadmill-sdk.h ../ios/TreadmillSDK/libtml/

OUTPUT_PATH=$DST_DIR/$LIB_NAME.xcframework
xcodebuild -create-xcframework \
  -library target/aarch64-apple-ios/release/lib$LIB_NAME.a -headers $HEADER_DIR \
  -library $SIM_LIB -headers $HEADER_DIR \
  -output $OUTPUT_PATH

rm -rf ios

# 在 XCFramework 中添加模块映射
mkdir -p $OUTPUT_PATH/Modules
cp -fv ../ios/treadmill_sdk.modulemap $OUTPUT_PATH/Modules/module.modulemap

mkdir -p ../ios/dist/
cp -rf $OUTPUT_PATH ../ios/dist/

echo_y "C Lib xcframework created: $DST_DIR/$LIB_NAME.xcframework"

# echo_y $PWD
# 编译TreaddmillSDK
./scripts/build_ios_framework.sh
