#!/bin/bash

HOST_NAME=com.example.nativehost
HOST_JSON="$(realpath ../native/host.json)"
MAIN_SCRIPT="$(realpath ../native/main.py)"
TARGET_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
TARGET_FILE="$TARGET_DIR/$HOST_NAME.json"

mkdir -p "$TARGET_DIR"

# Replace placeholder in host.json with the actual Python script path
sed "s@__REPLACED_BY_INSTALL_SCRIPT__@$MAIN_SCRIPT@" "$HOST_JSON" > "$TARGET_FILE"

echo "설치 완료: $TARGET_FILE"
