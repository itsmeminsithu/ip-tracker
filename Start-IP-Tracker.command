#!/bin/bash
# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
cd -- "$(dirname -- "$0")" || exit 1
PYTHON_BIN=""
for candidate in python3 python3.14 python3.13 python3.12 python3.11 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  echo "Install Python 3.11 or newer from https://www.python.org/downloads/ then try again."
  read -r -p "Press Enter to close."
  exit 1
fi
"$PYTHON_BIN" launch.py
status=$?
if [ "$status" -ne 0 ]; then read -r -p "Press Enter to close."; fi
exit "$status"
