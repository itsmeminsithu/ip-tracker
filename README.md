# IP Tracker

A local IP address dashboard by **Min SiThu (devminsithu)**.

[Website](https://minsithu.org/) · [Contact](https://minsithu.org/contact/) · [MIT License](LICENSE)

It shows the IPv4, IPv6 and MAC addresses of the machine it runs on, detects your public IPs, and looks up location and network details for an address you enter.

## What it shows

- Local IPv4 and IPv6 addresses, grouped by network adapter
- Current MAC address, connection status, MTU and subnet masks
- Public IPv4 and IPv6 detection, done separately
- For a public IP lookup: approximate country, region, city, ISP, organization, ASN and timezone
- Local classification of private, loopback, link-local, multicast and special-use addresses
- A 3D globe you can zoom, rotate and recenter, with 2D/3D controls
- Google Maps and satellite-view links for the returned coordinates
- Copyable address blocks, JSON downloads, CSV export of lookup history
- The last 100 lookups that succeeded, kept in session memory
- Launchers for Mac, Windows and Linux that install dependencies on first run
- Tests (pytest)

## Quick start

You need Python 3.11 or newer. Clone the repo, then use the launcher for your system:

| System | Start |
| --- | --- |
| macOS | Double-click `Start-IP-Tracker.command`, or run `bash Start-IP-Tracker.command` in Terminal |
| Windows | Double-click `Start-IP-Tracker.bat` |
| Linux | Run `sh start-ip-tracker.sh` |

First run creates `.venv` and installs requirements, so you need internet for setup. If the browser does not open, go to **http://127.0.0.1:8502**. Leave the terminal open; **Ctrl+C** stops it.

Troubleshooting is in [QUICKSTART.md](QUICKSTART.md).

## Trying it in Codespaces

This is a Streamlit app, so it cannot run on GitHub Pages. Codespaces works:

1. On GitHub, click **Code → Codespaces → Create codespace on main** (after this change is merged).
2. The devcontainer installs `requirements.txt` and forwards port **8502**.
3. In the Codespaces terminal: `python -m streamlit run app.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true`.
4. Open forwarded port **8502** in the Ports panel.

## Manual install

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port=8502
```

Windows Command Prompt:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port=8502
```

## Using it

1. **My device** lists the machine's adapters. Pick your Wi-Fi, Ethernet or VPN adapter to see its addresses. Use **Refresh device** after a network change.
2. **Detect public IPs** asks ipify for the internet-facing IPv4 and IPv6 addresses. A VPN or proxy changes what comes back. An IPv6 failure shows on its own; it does not take the IPv4 result down with it.
3. **IP lookup** takes one IPv4 or IPv6 address. Public addresses go to ipwho.is. Other types are classified locally, with no geolocation request.
4. When there are coordinates, **Location explorer** puts an approximate marker on the 3D globe. Drag and scroll, or use the Google Maps buttons. The globe is OpenStreetMap streets on an ellipsoid — not Google Earth imagery, not terrain elevation, not 3D buildings.
5. **Lookup history** holds the last 100 completed lookups. Export to CSV or clear it.

Two things that trip people up: the first adapter in the list is just a convenience pick, not a checked default route, so select the adapter you are actually using. And a device can have several IPv6 addresses. Link-local IPv6 addresses in the device panel may carry a zone ID like `%en0`; the lookup box wants an IP literal without one. Virtual adapters and VPNs are included in the list.

## Reading the results

- **Local IP:** an address on an adapter of the computer running this Python app.
- **Public IP:** the address an external service sees. It may belong to a router, VPN or proxy.
- **MAC:** the link-layer address the OS reports right now. It may be randomized or virtual, and some adapters do not report one. It is not necessarily the factory hardware address.
- **IP location:** an estimate for the network. Not GPS, not a person's identity, not an exact street address.
- **Remote MAC:** you cannot get one from a public IP lookup. This app only shows local adapter MAC addresses.
- **No IPv6 detected:** the request failed, or nothing usable came back. On its own that does not prove IPv6 is disabled.

Classification uses Python's `ipaddress` module. Some special-use classifications differ between Python versions.

## Privacy, and what leaves your machine

By default the server listens only on `127.0.0.1`. The device panel describes the **host running the app**, not whoever opens the page. Do not put this up as a public site to collect visitor MAC addresses; browsers do not hand those out anyway.

The device panel works offline once setup is done. It reads OS interface metadata with psutil and does not scan the LAN. Nothing is looked up just by opening the app: public-IP detection and geolocation only run when you press the button.

- **ipify:** gets public IP detection requests at `api.ipify.org` and `api6.ipify.org`.
- **ipwho.is:** gets the public address you enter for a lookup, plus your connection's public IP.
- **3D map:** your browser loads CesiumJS from cesium.com and visible map tiles from OpenStreetMap. Tile requests show the area being viewed and the browser's connection IP. They do not include the searched IP or local MAC addresses. Google links open the returned coordinates on Google Maps when you click them. The map needs internet and WebGL; if it fails to load, the lookup results stay and the Google Maps links still work. No API key is needed for the included globe. OpenStreetMap tiles are for normal interactive viewing — do not bulk-download or prefetch them. For heavier use, get a tile provider that fits your traffic.
- Local MAC addresses and the full device snapshot are never sent to either provider.
- No database, account, API key or analytics of my own. Streamlit usage telemetry is disabled.
- Lookups and device snapshots live in session memory. Closing, reconnecting or restarting can clear them.
- Exports can contain device addresses. Read them before you share them. Git ignores the default export filenames.

Providers have their own terms, rate limits and availability. Timeouts, rate limits, bad responses and missing IPv6 are handled without making up a result.

Provider docs:
- https://www.ipify.org/
- https://ipwhois.io/documentation
- https://psutil.readthedocs.io/

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests mock OS data and external services where that makes sense. They cover address classification, IPv6, MAC display, provider failures, export escaping and dashboard interactions.

## Files

- `app.py`: dashboard and session state
- `iptracker/core.py`: local interfaces, IP validation, external providers
- `iptracker/maps.py` and `iptracker/globe.html`: coordinate validation and the Cesium globe
- `iptracker/export.py`: CSV and JSON exports
- `launch.py`: environment setup and app startup
- `test_*.py`: tests
- `.devcontainer/devcontainer.json`: Codespaces preview (port 8502)

## Author and license

Copyright © 2026 **Min SiThu (devminsithu)**.

[minsithu.org](https://minsithu.org/) · [Contact](https://minsithu.org/contact/)

Source is under the [MIT License](LICENSE). Dependencies keep their own licenses.

Map libraries: CesiumJS 1.146 loads from the official CDN and keeps its Apache-2.0 license. Map data © OpenStreetMap contributors; attribution stays visible in the viewer. Google Maps is an external service, not bundled code.

- https://cesium.com/learn/cesiumjs/
- https://www.openstreetmap.org/copyright
- https://operations.osmfoundation.org/policies/tiles/
- https://developers.google.com/maps/documentation/urls/get-started
