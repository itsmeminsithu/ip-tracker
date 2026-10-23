"""IP Tracker by Min SiThu (devminsithu) — https://minsithu.org/
Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
"""
import streamlit as st
import streamlit.components.v1 as components
from iptracker.maps import location_coordinates, globe_html, google_maps_url, google_satellite_url
from iptracker.core import LookupError, device_snapshot, public_snapshot, lookup_ip
from iptracker.export import csv_bytes, json_bytes

st.set_page_config(page_title='IP Tracker · Min SiThu', page_icon='◎', layout='wide')
st.markdown('''<style>
.block-container{max-width:1240px;padding-top:2.5rem}
h1{letter-spacing:-.05em;font-weight:750!important}
[data-testid="stSidebar"]{border-right:1px solid #26344B}
[data-testid="stMetric"]{border:1px solid #33445E;border-radius:14px;padding:16px;background:#162238}
[data-testid="stMetricValue"]{font-size:1.35rem;overflow-wrap:anywhere}
[data-testid="stCode"]{border:1px solid #33445E;border-radius:10px}
</style>''', unsafe_allow_html=True)
st.session_state.setdefault('history', [])


def refresh_device():
    try:
        st.session_state.device = device_snapshot()
        st.session_state.pop('device_error', None)
    except (OSError, RuntimeError) as exc:
        st.session_state.device_error = f'Could not read network interfaces: {exc}'
        st.session_state.pop('device', None)


if 'device' not in st.session_state and 'device_error' not in st.session_state:
    refresh_device()

with st.sidebar:
    st.markdown('## ◎ IP Tracker')
    st.caption('BY MIN SITHU')
    st.divider()
    st.write('Your network identity, in one place.')
    st.caption('Local IPv4 · IPv6 · MAC\n\nPublic IP · Location · ISP')
    st.divider()
    st.markdown('**Min SiThu**  \n@devminsithu')
    st.markdown('[Website](https://minsithu.org/) · [Contact](https://minsithu.org/contact/)')
    st.caption('v1.0.0 · MIT License\n\n© 2026 Min SiThu')

st.caption('NETWORK UTILITIES / 01')
st.title('IP Tracker')
st.write('View your device addresses and look up an IPv4 or IPv6 address.')
st.caption('Device information belongs to the computer running this app. Run locally to see your own device.')
device_tab, lookup_tab, history_tab = st.tabs(['My device', 'IP lookup', 'Lookup history'])

with device_tab:
    head, refresh = st.columns([4, 1])
    with head:
        st.subheader('Your device')
    with refresh:
        if st.button('Refresh device', use_container_width=True):
            refresh_device()
            st.rerun()
    if 'device_error' in st.session_state:
        st.error(st.session_state.device_error)
    device = st.session_state.get('device')
    if device:
        st.caption(f"{device['hostname']} · {device['system']} · Captured {device['captured_at']}")
        adapters = device['interfaces']
        if not adapters:
            st.info('No network adapters were reported by the operating system.')
        else:
            selection = st.selectbox('Network adapter', [a['name'] for a in adapters])
            adapter = next(a for a in adapters if a['name'] == selection)
            st.caption(f"{adapter['status']} · MTU {adapter['mtu'] or 'Unknown'} · Select an adapter to see its addresses.")
            ipv4, ipv6, mac = st.columns(3)
            for col, title, addresses in [(ipv4, 'LOCAL IPv4', adapter['ipv4']), (ipv6, 'LOCAL IPv6', adapter['ipv6'])]:
                with col:
                    st.markdown(f'**{title}**')
                    if addresses:
                        for entry in addresses:
                            st.code(entry['address'], language=None)
                            st.caption(entry['scope'])
                    else:
                        st.caption('No address assigned')
            with mac:
                st.markdown('**MAC ADDRESS**')
                if adapter['mac']:
                    for address in adapter['mac']:
                        st.code(address, language=None)
                else:
                    st.caption('Not reported for this adapter')
                st.caption('Current interface address; it may be randomized or virtual.')
            with st.expander('All adapters and subnet masks'):
                flat = []
                for a in adapters:
                    for family in ('ipv4', 'ipv6'):
                        for entry in a[family]:
                            flat.append({'Adapter': a['name'], 'Status': a['status'], 'Type': family.upper(),
                                         'Address': entry['address'], 'Netmask': entry['netmask'],
                                         'Scope': entry['scope'], 'MAC': ', '.join(a['mac']) or 'Not reported'})
                    if not a['ipv4'] and not a['ipv6']:
                        flat.append({'Adapter': a['name'], 'Status': a['status'], 'Type': '—',
                                     'Address': 'Not assigned', 'Netmask': None, 'Scope': '—',
                                     'MAC': ', '.join(a['mac']) or 'Not reported'})
                st.dataframe(flat, hide_index=True, use_container_width=True)
        st.download_button('Download device details (JSON)', json_bytes(device), 'ip-tracker-device.json', 'application/json')
    st.divider()
    st.subheader('Public IP addresses')
    st.caption('Detect sends requests to ipify. A VPN or proxy may change the addresses shown. Local MAC addresses are not sent.')
    if st.button('Detect public IPs', type='primary'):
        with st.spinner('Checking IPv4 and IPv6 connectivity…'):
            st.session_state.public = public_snapshot()
    public = st.session_state.get('public')
    if public:
        for col, key, label in zip(st.columns(2), ('ipv4', 'ipv6'), ('PUBLIC IPv4', 'PUBLIC IPv6')):
            with col:
                st.markdown(f'**{label}**')
                item = public[key]
                if item['ip']:
                    st.code(item['ip'], language=None)
                else:
                    st.info('Not detected')
                    st.caption(item['error'])
        st.caption('Detected ' + public['captured_at'] + ' · Refresh after changing networks or VPN.')
    else:
        st.caption('Press Detect public IPs to check your internet-facing addresses.')

with lookup_tab:
    st.subheader('Look up an IP address')
    st.caption('Public IP lookups send the entered address to ipwho.is. Private and special-use addresses are classified locally.')
    with st.form('lookup'):
        target = st.text_input('IPv4 or IPv6 address', placeholder='8.8.8.8 or 2606:4700:4700::1111', max_chars=64)
        submitted = st.form_submit_button('Look up address →', type='primary')
    if submitted:
        st.session_state.pop('lookup_result', None)
        try:
            with st.spinner('Looking up address…'):
                record = lookup_ip(target)
            st.session_state.lookup_result = record
            st.session_state.history = (st.session_state.history + [record])[-100:]
        except ValueError as exc:
            st.error(str(exc))
        except LookupError as exc:
            st.error(str(exc))
    record = st.session_state.get('lookup_result')
    if record:
        st.code(record['ip'], language=None)
        a, b, c = st.columns(3)
        a.metric('Address type', record['version'])
        b.metric('Address scope', record['scope'])
        c.metric('Country', record.get('country') or 'Not available')
        st.info(record['message'])
        if record['public']:
            st.table({'Field': ['City (approximate)', 'Region', 'ISP', 'Organization', 'ASN', 'Timezone', 'Source'],
                      'Value': [record.get(k) or 'Not available' for k in ('city', 'region', 'isp', 'organization', 'asn', 'timezone', 'source')]})
        coordinates = location_coordinates(record)
        if coordinates:
            lat, lon = coordinates
            st.subheader('Location explorer')
            st.caption('Approximate network location. The globe uses OpenStreetMap tiles; Google Maps opens separately.')
            components.html(globe_html(lat, lon), height=520, scrolling=False)
            maps, satellite = st.columns(2)
            with maps:
                st.link_button('Open in Google Maps ↗', google_maps_url(lat, lon), use_container_width=True)
            with satellite:
                st.link_button('Google satellite view ↗', google_satellite_url(lat, lon), use_container_width=True)
        elif record['public']:
            st.caption('The provider returned no usable coordinates for this address.')
        with st.expander('Address details'):
            st.write('Expanded address')
            st.code(record['expanded'], language=None)
            st.caption('Checked ' + record['checked_at'])
        st.download_button('Download lookup (JSON)', json_bytes(record), 'ip-tracker-lookup.json', 'application/json')
    st.caption('IP lookup cannot identify a person, an exact home address, or a remote device’s MAC address.')

with history_tab:
    st.subheader('Lookup history')
    history = st.session_state.history
    if history:
        st.dataframe([{k: r.get(k, '') for k in ('checked_at', 'ip', 'version', 'scope', 'country', 'city', 'isp')}
                      for r in reversed(history)], hide_index=True, use_container_width=True)
        download, clear = st.columns([1, 3])
        with download:
            st.download_button('Export CSV', csv_bytes(history), 'ip-tracker-history.csv', 'text/csv')
        with clear:
            if st.button('Clear history'):
                st.session_state.history = []
                st.session_state.pop('lookup_result', None)
                st.rerun()
    else:
        st.caption('Your completed lookups will appear here.')
    st.caption('The last 100 lookups are kept in this session only. Export before closing the app.')
