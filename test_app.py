# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from iptracker.core import LookupError

APP = str(Path(__file__).resolve().parents[1] / 'app.py')
DEVICE = {'captured_at': '2026-10-23T00:00:00Z', 'hostname': 'Test Mac', 'system': 'Darwin',
          'interfaces': [{'name': 'en0', 'status': 'Up', 'mtu': 1500, 'mac': ['aa:bb:cc:dd:ee:ff'],
                          'ipv4': [{'address': '192.168.1.5', 'netmask': '255.255.255.0', 'scope': 'Private / special-use'}],
                          'ipv6': []}]}


def button(app, label):
    return next(b for b in app.button if b.label == label)


def test_local_render_no_external_requests():
    with patch('iptracker.core.device_snapshot', return_value=DEVICE), patch('requests.get') as get:
        app = AppTest.from_file(APP).run()
        assert not app.exception
        assert app.selectbox[0].value == 'en0'
        assert any(c.value == 'aa:bb:cc:dd:ee:ff' for c in app.code)
        get.assert_not_called()


def test_lookup_validation_private_history_and_clear():
    with patch('iptracker.core.device_snapshot', return_value=DEVICE), patch('requests.get') as get:
        app = AppTest.from_file(APP).run()
        button(app, 'Look up address →').click().run()
        assert app.error
        app.text_input[0].set_value('192.168.1.1')
        button(app, 'Look up address →').click().run()
        assert not app.exception
        assert len(app.session_state['history']) == 1
        button(app, 'Clear history').click().run()
        assert not app.exception
        assert app.session_state['history'] == []
        get.assert_not_called()


def test_public_detection_button():
    public = {'captured_at': 'now', 'ipv4': {'ip': '8.8.8.8', 'error': None},
              'ipv6': {'ip': None, 'error': 'IPv6 unavailable'}}
    with patch('iptracker.core.device_snapshot', return_value=DEVICE), patch('iptracker.core.public_snapshot', return_value=public):
        app = AppTest.from_file(APP).run()
        button(app, 'Detect public IPs').click().run()
        assert not app.exception
        assert app.session_state['public']['ipv4']['ip'] == '8.8.8.8'


def test_provider_error_is_displayed():
    with patch('iptracker.core.device_snapshot', return_value=DEVICE), patch('iptracker.core.lookup_ip', side_effect=LookupError('Provider timed out')):
        app = AppTest.from_file(APP).run()
        app.text_input[0].set_value('8.8.8.8')
        button(app, 'Look up address →').click().run()
        assert not app.exception
        assert app.error[0].value == 'Provider timed out'


def test_no_adapters_and_refresh():
    with patch('iptracker.core.device_snapshot', return_value={**DEVICE, 'interfaces': []}):
        app = AppTest.from_file(APP).run()
        button(app, 'Refresh device').click().run()
        assert not app.exception
        assert not app.selectbox


def test_lookup_renders_globe():
    row = {'ip': '8.8.8.8', 'version': 'IPv4', 'scope': 'Public', 'public': True,
           'expanded': '8.8.8.8', 'country': 'Example', 'message': 'Approximate location',
           'latitude': 13.75, 'longitude': 100.5, 'checked_at': 'now', 'source': 'ipwho.is'}
    with patch('iptracker.core.device_snapshot', return_value=DEVICE), patch('iptracker.core.lookup_ip', return_value=row):
        app = AppTest.from_file(APP).run()
        app.text_input[0].set_value('8.8.8.8')
        button(app, 'Look up address →').click().run()
        assert not app.exception
        assert any(h.value == 'Location explorer' for h in app.subheader)
        assert len(app.get('iframe')) == 1


def test_device_permission_error_is_handled():
    with patch('iptracker.core.device_snapshot', side_effect=PermissionError('Access denied')):
        app = AppTest.from_file(APP).run()
        assert not app.exception
        assert 'Could not read network interfaces' in app.error[0].value
        assert app.text_input[0].label == 'IPv4 or IPv6 address'
