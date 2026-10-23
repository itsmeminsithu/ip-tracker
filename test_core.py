# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
import socket
from types import SimpleNamespace
from unittest.mock import patch

import psutil
import pytest
import requests
from iptracker.core import (LookupError, _json_request, detect_public_ip, device_snapshot,
                            inspect_ip, lookup_ip, parse_ip, public_snapshot, scope)


@pytest.mark.parametrize('value', ['', 'https://8.8.8.8', '8.8.8.8:443', '8.8.8.8/24', 'fe80::1%en0', 'example.com', '999.1.1.1'])
def test_invalid(value):
    with pytest.raises(ValueError):
        parse_ip(value)


@pytest.mark.parametrize('value,expected', [('127.0.0.1', 'Loopback'), ('::1', 'Loopback'),
    ('192.168.0.1', 'Private / special-use'), ('fe80::1%en0', 'Link-local'),
    ('100.64.0.1', 'Shared / CGNAT'), ('0.0.0.0', 'Unspecified'),
    ('224.0.0.1', 'Multicast'), ('8.8.8.8', 'Public'), ('2606:4700:4700::1111', 'Public')])
def test_scope(value, expected):
    assert scope(value) == expected


def test_canonical_ipv6():
    assert inspect_ip(' 2606:4700:4700:0:0:0:0:1111 ')['ip'] == '2606:4700:4700::1111'


def test_private_never_sent_to_provider():
    with patch('requests.get') as get:
        for ip in ('10.0.0.1', '::1', '100.64.0.1', '224.0.0.1', '2001:db8::1'):
            assert lookup_ip(ip)['source'] == 'Local classification'
        get.assert_not_called()


def test_device_adapter_grouping():
    def address(family, value):
        return SimpleNamespace(family=family, address=value, netmask=None)
    interfaces = {'lo0': [address(socket.AF_INET, '127.0.0.1')],
                  'en0': [address(socket.AF_INET, '192.168.1.2'), address(socket.AF_INET6, 'fe80::123%en0'),
                          address(psutil.AF_LINK, 'AA-BB-CC-DD-EE-FF')],
                  'utun0': [address(psutil.AF_LINK, '00:00:00:00:00:00')]}
    stats = {name: SimpleNamespace(isup=True, mtu=1500) for name in interfaces}
    with patch('psutil.net_if_addrs', return_value=interfaces), patch('psutil.net_if_stats', return_value=stats):
        data = device_snapshot()['interfaces']
    assert data[0]['name'] == 'en0'
    assert data[0]['ipv6'][0]['address'] == 'fe80::123%en0'
    assert data[0]['mac'] == ['aa:bb:cc:dd:ee:ff']
    assert next(a for a in data if a['name'] == 'utun0')['mac'] == []


def test_no_adapters():
    with patch('psutil.net_if_addrs', return_value={}), patch('psutil.net_if_stats', return_value={}):
        assert device_snapshot()['interfaces'] == []


def test_public_family_validation():
    with patch('iptracker.core._json_request', return_value={'ip': '8.8.8.8'}):
        assert detect_public_ip(4)['ip'] == '8.8.8.8'
        assert detect_public_ip(6)['ip'] is None


def test_ipv6_failure_does_not_hide_ipv4():
    def provider(url):
        if 'api6' in url:
            raise LookupError('Connection failed')
        return {'ip': '8.8.8.8'}
    with patch('iptracker.core._json_request', side_effect=provider):
        data = public_snapshot()
    assert data['ipv4']['ip'] == '8.8.8.8'
    assert data['ipv6']['ip'] is None


def test_lookup_fields():
    payload = {'ip': '8.8.8.8', 'success': True, 'country': 'United States', 'city': 'Example',
               'connection': {'isp': 'Example ISP', 'asn': 15169}, 'timezone': {'id': 'Etc/UTC'}}
    with patch('iptracker.core._json_request', return_value=payload) as get:
        row = lookup_ip('8.8.8.8')
    get.assert_called_once_with('https://ipwho.is/8.8.8.8')
    assert row['isp'] == 'Example ISP'
    assert row['asn'] == '15169'


@pytest.mark.parametrize('payload', [{'success': False}, {'success': True, 'ip': '1.1.1.1'},
                                    {'success': True, 'ip': 'invalid'},
                                    {'success': True, 'ip': '8.8.8.8', 'connection': ['invalid']}])
def test_bad_lookup_response(payload):
    with patch('iptracker.core._json_request', return_value=payload), pytest.raises(LookupError):
        lookup_ip('8.8.8.8')


@pytest.mark.parametrize('code', [429, 500, 302])
def test_http_errors(code):
    with patch('requests.get', return_value=SimpleNamespace(status_code=code)), pytest.raises(LookupError):
        _json_request('https://ipwho.is/8.8.8.8')


@pytest.mark.parametrize('error', [requests.Timeout(), requests.ConnectionError()])
def test_connection_errors(error):
    with patch('requests.get', side_effect=error), pytest.raises(LookupError):
        _json_request('https://ipwho.is/8.8.8.8')


def test_invalid_json():
    with patch('requests.get') as get:
        get.return_value.status_code = 200
        get.return_value.json.side_effect = ValueError('bad json')
        with pytest.raises(LookupError):
            _json_request('https://ipwho.is/8.8.8.8')


def test_non_object_json():
    with patch('requests.get') as get:
        get.return_value.status_code = 200
        get.return_value.json.return_value = []
        with pytest.raises(LookupError):
            _json_request('https://ipwho.is/8.8.8.8')
