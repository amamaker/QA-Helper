#!/bin/bash
unauthorized_contents=$(awk '{$1=""; $2=""; gsub(/^[ \t]+/,""); print $0}' /unauthorized.list)
target_file="/usb_authorized.list"

if [ ! -f "$target_file" ]; then
  touch "$target_file"
fi

echo "$unauthorized_contents" | cat - "$target_file" > temp && mv temp "$target_file"