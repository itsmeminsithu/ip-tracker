"""Local interface inventory and IP intelligence.
Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
"""
import ipaddress
import math
import platform
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import psutil
import requests

TIMEOUT = (4, 7)
PUBLIC_ENDPOINTS = {
    4: 'https://api.ipify.org?format=json',
    6: 'https://api6.ipify.org?format=json',
}


class LookupError(Exception):
    """An external provider could not return a usable result."""


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def parse_ip(value):
    value = value.strip()
    if not value or '%' in value or '/' in value:
        raise ValueError('Enter one IPv4 or IPv6 address without a URL, port, zone ID or subnet prefix.')
    try:
        return ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError('Enter a valid IPv4 or IPv6 address, such as 8.8.8.8 or 2606:4700:4700::1111.') from exc


def scope(address):
    ip = ipaddress.ip_address(str(address).split('%', 1)[0])
    if ip.is_unspecified:
        return 'Unspecified'
    if ip.is_loopback:
        return 'Loopback'
    if ip.is_multicast:
        return 'Multicast'
    if ip.is_link_local:
        return 'Link-local'
    if ip.version == 4 and ip in ipaddress.ip_network('100.64.0.0/10'):
        return 'Shared / CGNAT'
    if ip.is_reserved:
        return 'Reserved'
    if ip.is_private:
        return 'Private / special-use'
    return 'Public' if ip.is_global else 'Special-use'


def inspect_ip(value):
    ip = parse_ip(value)
    kind = scope(ip)
    return {
        'ip': str(ip), 'version': f'IPv{ip.version}', 'scope': kind,
        'expanded': ip.exploded, 'public': kind == 'Public',
    }


def device_snapshot():
    """Only reads OS interface metadata. Does not send packets or scan the LAN."""
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    adapters = []
    for name, entries in interfaces.items():
        status = stats.get(name)
        item = {'name': name, 'status': 'Up' if status and status.isup else 'Down / unknown',
                'mtu': status.mtu if status else None, 'mac': [], 'ipv4': [], 'ipv6': []}
        for entry in entries:
            if entry.family in (socket.AF_INET, socket.AF_INET6):
                family = 'ipv4' if entry.family == socket.AF_INET else 'ipv6'
                item[family].append({'address': entry.address, 'netmask': entry.netmask,
                                     'scope': scope(entry.address)})
            elif entry.family == psutil.AF_LINK and entry.address:
                mac = entry.address.replace('-', ':').lower()
                if set(mac.replace(':', '')) != {'0'}:
                    item['mac'].append(mac)
        adapters.append(item)
    def rank(item):
        usable = any(a['scope'] not in ('Loopback', 'Unspecified') for a in item['ipv4'] + item['ipv6'])
        return (item['status'] != 'Up', not usable, item['name'])
    adapters.sort(key=rank)
    return {'captured_at': timestamp(), 'hostname': socket.gethostname(),
            'system': platform.system(), 'interfaces': adapters}


def _json_request(url):
    try:
        response = requests.get(url, timeout=TIMEOUT, allow_redirects=False,
                                headers={'Accept': 'application/json', 'User-Agent': 'IPTracker/1.0'})
        if response.status_code == 429:
            raise LookupError('Provider rate limit reached. Wait and try again later.')
        if response.status_code != 200:
            raise LookupError(f'Provider returned HTTP {response.status_code}. Try again later.')
        data = response.json()
    except requests.Timeout as exc:
        raise LookupError('The provider timed out. Check your connection and retry.') from exc
    except requests.RequestException as exc:
        raise LookupError('Could not connect securely to the provider. Check your network or VPN.') from exc
    except ValueError as exc:
        raise LookupError('The provider returned an invalid response.') from exc
    if not isinstance(data, dict):
        raise LookupError('The provider returned an unexpected response format.')
    return data


def detect_public_ip(version):
    try:
        payload = _json_request(PUBLIC_ENDPOINTS[version])
        address = parse_ip(str(payload.get('ip', '')))
        if address.version != version or scope(address) != 'Public':
            raise ValueError('Unexpected address family or scope')
        return {'ip': str(address), 'error': None}
    except (LookupError, ValueError) as exc:
        message = str(exc)
        if version == 6:
            message += ' IPv6 may be unavailable on this connection; this alone does not prove it is disabled.'
        return {'ip': None, 'error': message}


def public_snapshot():
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(detect_public_ip, (4, 6)))
    return {'captured_at': timestamp(), 'ipv4': results[0], 'ipv6': results[1]}


def lookup_ip(value):
    """Geolocation only sends canonical public IP literals to a fixed HTTPS provider."""
    local = inspect_ip(value)
    base = {**local, 'checked_at': timestamp(), 'source': 'Local classification'}
    if not local['public']:
        return {**base, 'message': 'This is not a public unicast address. No geolocation request was sent.'}
    payload = _json_request('https://ipwho.is/' + local['ip'])
    if payload.get('success') is not True:
        raise LookupError('The provider could not locate this IP address. Try another address or retry later.')
    try:
        returned_ip = parse_ip(str(payload.get('ip', '')))
    except ValueError as exc:
        raise LookupError('Provider response did not contain a valid IP address.') from exc
    if str(returned_ip) != local['ip']:
        raise LookupError('Provider response did not match the requested IP address.')
    connection = payload.get('connection') or {}
    timezone_info = payload.get('timezone') or {}
    if not isinstance(connection, dict) or not isinstance(timezone_info, dict):
        raise LookupError('Provider response contained invalid network metadata.')
    def text(value):
        return str(value) if value is not None else ''
    latitude = coordinate(payload.get('latitude'), -90, 90)
    longitude = coordinate(payload.get('longitude'), -180, 180)
    return {**base, 'source': 'ipwho.is', 'latitude': latitude, 'longitude': longitude,
            'country': text(payload.get('country')), 'region': text(payload.get('region')),
            'city': text(payload.get('city')), 'isp': text(connection.get('isp')),
            'organization': text(connection.get('org')), 'asn': text(connection.get('asn')),
            'timezone': text(timezone_info.get('id')),
            'message': 'Location is an estimate for the network address, not a person or exact device location.'}


def coordinate(value, minimum, maximum):
    if isinstance(value, bool) or value is None:
        return None
    try:
        value = float(value)
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) and minimum <= value <= maximum else None
