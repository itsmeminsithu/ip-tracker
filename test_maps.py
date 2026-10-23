# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
import pytest
from iptracker.core import coordinate
from iptracker.maps import globe_html, location_coordinates, google_maps_url, google_satellite_url


@pytest.mark.parametrize('value', [None, True, 'NaN', 'Infinity', -91, 91, '<script>'])
def test_reject_invalid_latitude(value):
    assert coordinate(value, -90, 90) is None


def test_zero_is_valid():
    assert location_coordinates({'latitude': 0, 'longitude': 0}) == (0.0, 0.0)


def test_missing_coordinates():
    assert location_coordinates({'latitude': 5}) is None


def test_map_links_and_html():
    assert 'api=1' in google_maps_url(13.75, 100.5)
    assert 'basemap=satellite' in google_satellite_url(13.75, 100.5)
    html = globe_html(13.75, 100.5)
    assert '__COORDINATES__' not in html
    assert '13.75' in html
    assert 'OpenStreetMap' in html
    assert 'Approximate IP location' in html


def test_map_rejects_script_input():
    with pytest.raises(ValueError):
        globe_html('</script><script>alert(1)</script>', 5)
