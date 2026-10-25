"""Portable exports. Copyright (c) 2026 Min SiThu (devminsithu).
SPDX-License-Identifier: MIT
"""
import csv
import io
import json


def json_bytes(value):
    return json.dumps(value, indent=2, ensure_ascii=False).encode('utf-8')


def csv_bytes(rows):
    fields = ('checked_at', 'ip', 'version', 'scope', 'country', 'region', 'city',
              'isp', 'organization', 'asn', 'timezone', 'latitude', 'longitude', 'source')
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        safe = {}
        for field in fields:
            value = str(row.get(field, ''))
            if value.lstrip().startswith(('=', '+', '-', '@')):
                value = "'" + value
            safe[field] = value
        writer.writerow(safe)
    return output.getvalue().encode('utf-8-sig')
