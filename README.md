# IP Tracker

A local IP address dashboard by **Min SiThu (devminsithu)**.

[Website](https://minsithu.org/) · [Contact](https://minsithu.org/contact/) · [MIT License](LICENSE)

View your device's IPv4, IPv6 and MAC addresses, detect public IPs, and look up IP location and network information.

## Features

- Local IPv4 and IPv6 addresses grouped by network adapter
- Current MAC address, connection status, MTU and subnet masks
- Separate public IPv4 and IPv6 detection
- Public IP lookup: approximate country, region, city, ISP, organization, ASN and timezone
- Local classification of private, loopback, link-local, multicast and special-use addresses
- Interactive 3D globe with zoom, rotate, recenter and 2D/3D controls
- Google Maps and satellite-view links for returned coordinates
- Copyable address blocks, JSON downloads and CSV lookup-history export
- Last 100 successful lookups in session memory
- Mac, Windows and Linux launchers with first-run dependency installation
- Automated tests (pytest)

## Quick start

Requires Python 3.11 or newer. Clone the repository, then start it with the launcher for your system:

| System | Start |
| --- | --- |
| macOS | Double-click `Start-IP-Tracker.command`, or run `bash Start-IP-Tracker.command` in Terminal |
| Windows | Double-click `Start-IP-Tracker.bat` |
| Linux | Run `sh start-ip-tracker.sh` |

The launcher creates `.venv` and installs requirements on the first run.
Internet is required for setup. Open **http://127.0.0.1:8502** if your browser does not open.
Keep the terminal open. Press **Ctrl+C** to stop the app.

See [QUICKSTART.md](QUICKSTART.md) for troubleshooting.

## Live preview (GitHub Codespaces)

This is a Streamlit app, so it cannot run on GitHub Pages. Preview it in Codespaces instead:

1. On GitHub, click **Code → Codespaces → Create codespace on main** (after this change is merged).
2. The devcontainer installs `requirements.txt` automatically and forwards port **8502**.
3. In the Codespaces terminal, run `python -m streamlit run app.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true`.
4. Open the forwarded port **8502** from the Ports panel.

## Manual installation

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

## Usage

1. **My device** lists the computer's network adapters. Select your Wi-Fi, Ethernet or VPN adapter to see its addresses. Use **Refresh device** after a network change.
2. **Detect public IPs** contacts ipify to find the internet-facing IPv4 and IPv6 addresses. A VPN/proxy can change these results. An IPv6 failure is displayed independently of IPv4.
3. **IP lookup** accepts a single IPv4 or IPv6 address. Public addresses are sent to ipwho.is. Other address types are classified locally without a geolocation request.
4. When coordinates are available, the **Location explorer** shows an approximate marker on a 3D globe. Drag/scroll to explore or use the Google Maps buttons. The embedded globe uses OpenStreetMap streets on an ellipsoid, not Google Earth imagery, terrain elevation or 3D buildings.
5. **Lookup history** shows the last 100 completed lookups. Export to CSV or clear the history.

The first adapter is a convenience selection, not a verified default route.
Select the correct adapter for your connection. Virtual adapters and VPNs are included.
A device may have several IPv6 addresses. Link-local IPv6 addresses can include a zone ID
such as `%en0` in the device panel; the lookup input expects an IP literal without a zone ID.

## What the results mean

- **Local IP:** assigned to a network adapter on the computer running this Python app.
- **Public IP:** the address observed by an external service. It may belong to a router, VPN or proxy.
- **MAC:** the current link-layer address reported by the operating system. It may be randomized or virtual, and may be unavailable for some adapters. It is not necessarily the factory hardware address.
- **IP location:** an estimate for the network, not GPS, a person's identity or an exact street address.
- **Remote MAC:** cannot be obtained from an arbitrary public IP lookup. This app displays only local adapter MAC addresses.
- **No IPv6 detected:** the request failed or no usable result was returned. This alone does not prove IPv6 is disabled.

Classification uses Python's `ipaddress` module. Some special-use classifications can vary between Python versions.

## Privacy and services

The default server listens only on `127.0.0.1`. Device addresses describe the **host running the app**, not an arbitrary browser visitor. Do not deploy it as a public website for collecting visitor MAC addresses; browsers do not provide those addresses.

The embedded map needs Internet and WebGL support. If it cannot load, the app keeps the lookup results and offers Google Maps links. No API key is needed for the included globe. OpenStreetMap tiles are for normal interactive viewing; do not bulk-download or prefetch them. For larger deployments use a tile provider appropriate to your traffic.

The local device panel works offline after setup. It reads OS interface metadata with psutil and performs no LAN scan. Public-IP detection and geolocation are button-triggered; simply opening the app sends no application-level lookup requests.

- **ipify:** receives public IP detection requests at `api.ipify.org` and `api6.ipify.org`.
- **3D map:** your browser loads CesiumJS from cesium.com and visible map tiles from OpenStreetMap. Map tile requests reveal the area being viewed and the browser connection IP, but do not include the searched IP or local MAC addresses. Google links open the returned coordinates on Google Maps when clicked.
- **ipwho.is:** receives the public address entered for a lookup and the requesting connection's public IP.
- Local MAC addresses and the full device snapshot are never sent to either provider.
- No database, account, API key or custom analytics is required. Streamlit usage telemetry is disabled.
- Lookups and device snapshots are held in session memory. Closing/reconnecting or restarting may clear them.
- Exports may contain device addresses; review them before sharing. Git ignores default export filenames.

Providers have their own terms, rate limits and availability. The app handles timeouts, rate limits, invalid responses and unavailable IPv6 without inventing results.

Provider documentation:
- https://www.ipify.org/
- https://ipwhois.io/documentation
- https://psutil.readthedocs.io/

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests mock OS data and external services where appropriate. They cover address classification, IPv6, MAC display, provider failures, export escaping and dashboard interactions.

## Source structure

- `app.py`: dashboard and session state
- `iptracker/core.py`: local interfaces, IP validation and external providers
- `iptracker/maps.py` and `iptracker/globe.html`: coordinate validation and Cesium globe
- `iptracker/export.py`: CSV and JSON exports
- `launch.py`: environment setup and app startup
- `test_*.py`: automated tests
- `.devcontainer/devcontainer.json`: Codespaces preview (port 8502)


## Author and license

Copyright © 2026 **Min SiThu (devminsithu)**.

[minsithu.org](https://minsithu.org/) · [Contact](https://minsithu.org/contact/)

Project source is licensed under the [MIT License](LICENSE). Dependencies retain their own licenses.

## Map libraries and attribution

CesiumJS 1.146 loads from the official CDN and retains its Apache-2.0 license.
Map data © OpenStreetMap contributors; attribution remains visible in the viewer.
Google Maps is an external service, not bundled application code.

- https://cesium.com/learn/cesiumjs/
- https://www.openstreetmap.org/copyright
- https://operations.osmfoundation.org/policies/tiles/
- https://developers.google.com/maps/documentation/urls/get-started
