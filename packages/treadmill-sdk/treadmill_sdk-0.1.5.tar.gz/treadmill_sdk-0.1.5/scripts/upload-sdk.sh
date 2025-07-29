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
CARGO_PKG_VERSION=$(grep '^version =' Cargo.toml | awk -F'"' '{print $2}')

# 定义变量 LIB_VERSION
LIB_VERSION=$CARGO_PKG_VERSION

# 打印版本号以验证
echo "LIB_VERSION is $LIB_VERSION"

# 配置 OSS 上传所需的变量
accessKeyId='LTAIQGvJcHdwXeeZ'
accessKeySecret=$ALI_OSS_SECRET
endpoint='oss-cn-beijing.aliyuncs.com'
bucket="focus-resource"
cloudFolder="universal/treadmill/libs/v$LIB_VERSION"

# ================================================

declare -a result=()

function uploadFile() {
  local filePath="$1"
  local cloudPath="$cloudFolder/$(basename "$filePath")"
  local contentType=$(file -b --mime-type "$filePath")
  local dateValue="$(TZ=GMT env LANG=en_US.UTF-8 date +'%a, %d %b %Y %H:%M:%S GMT')"
  local stringToSign="PUT\n\n$contentType\n$dateValue\n/$bucket/$cloudPath"
  local signature=$(echo -en "$stringToSign" | openssl sha1 -hmac "$accessKeySecret" -binary | base64)
  local url="https://$bucket.$endpoint/$cloudPath"

  echo "Uploading $filePath to $url"

  curl -i -q -X PUT -T "$filePath" \
    -H "Content-Type: $contentType" \
    -H "Host: $bucket.$endpoint" \
    -H "Date: $dateValue" \
    -H "Authorization: OSS $accessKeyId:$signature" \
    "$url"

  result+=("$url")
}

# 检查是否提供了文件路径参数
if [ $# -lt 1 ]; then
  echo "Usage: $0 <file_to_upload1> [<file_to_upload2> ...]"
  exit 1
fi

# 上传所有文件
for file in "$@"; do
  if [ ! -f "$file" ]; then
    echo "Error: $file not found!"
    exit 1
  fi
  uploadFile "$file"
done

# 打印上传结果
for res in "${result[@]}"; do
  echo "$res"
done
