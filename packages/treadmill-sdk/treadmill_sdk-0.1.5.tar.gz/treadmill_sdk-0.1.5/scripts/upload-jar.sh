set -e # Exit on error

# Check platform compatibility
if [[ "$OSTYPE" == "msys" ]]; then
  echo -e "\033[0;31mError: This script does not support your platform ($OSTYPE)\033[0m"
  exit 1
fi

# Colorful echo functions
echo_y() { echo -e "\033[1;33m$*\033[0m"; } # Yellow
echo_r() { echo -e "\033[0;31m$*\033[0m"; } # Red

# Get the script's directory to handle paths relative to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到脚本所在目录（如果当前目录不是脚本所在目录）
[ "$(pwd)" != "$SCRIPT_DIR" ] && cd "$SCRIPT_DIR"
echo_y "current dir: $(pwd)"

cd ..

# Configuration
LIB_VERSION="0.1.2"

NAME="treadmill-sdk-$LIB_VERSION-release.jar"
SRC="../android/treadmilljna/lib/dist/$NAME"
cp -fv $SRC ./
./scripts/upload-sdk.sh $NAME
rm $NAME
echo_y "[treadmill-sdk] Upload complete."

