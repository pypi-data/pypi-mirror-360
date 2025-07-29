#!/bin/bash
set -e

# colorful echo functions
function echo_y() { echo -e "\033[1;33m$@\033[0m"; } # yellow
function echo_r() { echo -e "\033[0;31m$@\033[0m"; } # red

# Check Darwin Platform
platform=$(uname)
if [ "$platform" != "Darwin" ]; then
  echo_r "[iOS] Your platform $platform is not 'Darwin'"
  exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(dirname $0)"

# 切换到脚本所在目录（如果当前目录不是脚本所在目录）
[ "$(pwd)" != "$SCRIPT_DIR" ] && cd "$SCRIPT_DIR"
echo_y "current dir: $(pwd)"

cd ../../ios/TreadmillSDK

FRAMEWORK_NAME="TreadmillSDK"

echo_y "[iOS Framework] Start building iOS Framework."

# clean up 'build' and 'dist' folder
rm -rf build dist
mkdir -p "dist/${FRAMEWORK_NAME}-universal/"

# build 'iphoneos' and 'iphonesimulator' frameworks
PLATFORMS="iphoneos iphonesimulator"
for SDK in ${PLATFORMS}; do
  echo_y "Building '${SDK}' framework"
  xcodebuild clean build -quiet \
    -project "${FRAMEWORK_NAME}.xcodeproj" \
    -target ${FRAMEWORK_NAME} \
    -sdk ${SDK} \
    -configuration "Release" \
    ONLY_ACTIVE_ARCH=NO \
    IPHONEOS_DEPLOYMENT_TARGET="12.0" \
    CONFIGURATION_BUILD_DIR="./dist/${FRAMEWORK_NAME}-${SDK}"
done

# Create xcframwork combine of all frameworks
xcodebuild -create-xcframework \
  -framework ./dist/${FRAMEWORK_NAME}-iphonesimulator/${FRAMEWORK_NAME}.framework \
  -framework ./dist/${FRAMEWORK_NAME}-iphoneos/${FRAMEWORK_NAME}.framework \
  -output ./dist/${FRAMEWORK_NAME}-universal/${OUTPUT_DIR}/${FRAMEWORK_NAME}.xcframework

cp -rf ./dist/${FRAMEWORK_NAME}-universal/${FRAMEWORK_NAME}.xcframework ../dist/

# remove tmp files
echo "Clean up temporary files"
rm -rf build dist

# build complete
echo_y "[iOS Framework] build complete."

cd ../dist
ZIP_NAME=${FRAMEWORK_NAME}.xcframework.zip
# [ -f "$ZIP_NAME" ] && rm -f "$ZIP_NAME"
zip -r $ZIP_NAME ${FRAMEWORK_NAME}.xcframework
echo_y "[iOS Framework] zip file: $ZIP_NAME"
echo_y "[iOS Framework] zip file size: $(du -sh $ZIP_NAME)"
echo_y "[iOS Framework] zip file md5: $(md5 -q $ZIP_NAME)"
echo_y "[iOS Framework] zip file sha256: $(shasum -a 256 $ZIP_NAME | awk '{print $1}')"
mv $ZIP_NAME ../../rust/
../../rust/scripts/upload-sdk.sh $ZIP_NAME
rm -f ../../rust/$ZIP_NAME
echo_y "[iOS Framework] upload complete."
