#!/bin/bash
set -e # Exit on error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${SCRIPT_DIR}/dist"
VERSION_FILE="${SCRIPT_DIR}/VERSION"

# Configuration
LIB_VERSION="v0.1.2"
BASE_URL="https://app.brainco.cn/universal/treadmill/libs/${LIB_VERSION}"
# https://app.brainco.cn/universal/treadmill/libs/v0.1.2/win.zip

# Colorful echo functions
echo_y() { echo -e "\033[1;33m$*\033[0m"; } # Yellow
echo_r() { echo -e "\033[0;31m$*\033[0m"; } # Red

# Check if version is already installed
if [ -f "$VERSION_FILE" ] && grep -F --quiet "$LIB_VERSION" "$VERSION_FILE"; then
  echo_y "[treadmill-sdk] (${LIB_VERSION}) is already installed"
  cat "$VERSION_FILE"
  exit 0
fi

# Determine platform and library name
PLATFORM=$(uname)
case "$PLATFORM" in
"Linux")
  LIB_NAME="linux"
  ;;
"Darwin")
  LIB_NAME="mac"
  ;;
"msys" | "MINGW"*)
  LIB_NAME="win"
  ;;
*)
  echo_r "Error: This script does not support your platform ($PLATFORM)"
  exit 1
  ;;
esac

ZIP_NAME="${LIB_NAME}.zip"
DOWNLOAD_URL="${BASE_URL}/${ZIP_NAME}?$(date +%s)" # Timestamp for uniqueness

# Clean up previous files
echo_y "[treadmill-sdk] Cleaning up previous distribution..."
rm -rf "$DIST_DIR" "${SCRIPT_DIR}/__MACOSX" "${SCRIPT_DIR}/${ZIP_NAME}"

# Create dist directory
mkdir -p "$DIST_DIR"

# Download library
echo_y "[treadmill-sdk] Downloading (${LIB_VERSION}) for ${LIB_NAME}..."
if ! command -v wget >/dev/null 2>&1; then
  echo_r "Error: wget is not installed. Please install it and try again."
  exit 1
fi

wget -q --show-progress "$DOWNLOAD_URL" -O "${SCRIPT_DIR}/${ZIP_NAME}" || {
  echo_r "Error: Failed to download ${ZIP_NAME}"
  exit 1
}

# Extract and clean up
echo_y "[treadmill-sdk] Extracting ${ZIP_NAME}..."
unzip -o -q "${SCRIPT_DIR}/${ZIP_NAME}" -d "$SCRIPT_DIR" || {
  echo_r "Error: Failed to unzip ${ZIP_NAME}"
  exit 1
}
rm -f "${SCRIPT_DIR}/${ZIP_NAME}"
rm -rf "${SCRIPT_DIR}/__MACOSX"
rm -rf "${DIST_DIR}/__MACOSX"

# Create VERSION file
echo_y "[treadmill-sdk] Creating version file..."
cat >"$VERSION_FILE" <<EOF
[treadmill-sdk] Version: ${LIB_VERSION}
Update Time: $(date)
EOF

echo_y "[treadmill-${LIB_NAME}-sdk] (${LIB_VERSION}) downloaded successfully to ${DIST_DIR}"
