# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
import csv
import io
import json
from iptracker.export import csv_bytes, json_bytes


def test_csv_neutralizes_formula():
    row = next(csv.DictReader(io.StringIO(csv_bytes([{'isp': '=SUM(1,2)', 'city': 'A,B\nC'}]).decode('utf-8-sig'))))
    assert row['isp'] == "'=SUM(1,2)"
    assert row['city'] == 'A,B\nC'


def test_json_roundtrip():
    value = {'ipv6': 'fe80::1%en0', 'country': 'မြန်မာ'}
    assert json.loads(json_bytes(value)) == value
