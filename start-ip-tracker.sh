#!/bin/sh
# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
cd -- "$(dirname -- "$0")" || exit 1
exec python3 launch.py
