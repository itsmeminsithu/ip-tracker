"""Interactive 3D globe for approximate IP coordinates.
Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
"""
import json
from pathlib import Path
from urllib.parse import urlencode
from iptracker.core import coordinate


def location_coordinates(record):
    lat = coordinate(record.get('latitude'), -90, 90)
    lon = coordinate(record.get('longitude'), -180, 180)
    return (lat, lon) if lat is not None and lon is not None else None


def google_maps_url(lat, lon):
    if location_coordinates({'latitude': lat, 'longitude': lon}) is None:
        raise ValueError('Invalid coordinates')
    return 'https://www.google.com/maps/search/?' + urlencode({'api': '1', 'query': f'{lat},{lon}'})


def google_satellite_url(lat, lon):
    if location_coordinates({'latitude': lat, 'longitude': lon}) is None:
        raise ValueError('Invalid coordinates')
    return 'https://www.google.com/maps/@?' + urlencode({'api': '1', 'map_action': 'map',
            'center': f'{lat},{lon}', 'zoom': '11', 'basemap': 'satellite'})


def globe_html(lat, lon):
    coords = location_coordinates({'latitude': lat, 'longitude': lon})
    if coords is None:
        raise ValueError('Invalid coordinates')
    template = Path(__file__).with_name('globe.html').read_text(encoding='utf-8')
    # Only validated finite numbers enter the script; API strings are never embedded.
    return template.replace('__COORDINATES__', json.dumps({'lat': coords[0], 'lon': coords[1]}, allow_nan=False))
