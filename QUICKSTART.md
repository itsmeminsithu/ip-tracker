# Run IP Tracker

**Min SiThu (devminsithu)** · https://minsithu.org/ · https://minsithu.org/contact/

## Mac

1. Extract `IP-Tracker-Ready-to-Use.zip`.
2. Open the extracted **IP-Tracker** folder.
3. Double-click **Start-IP-Tracker.command**.
4. Wait for first-run setup, then open **http://127.0.0.1:8502**.

If double-clicking does not work:

1. Open Terminal.
2. Type `cd ` with a space, drag the **IP-Tracker** folder into Terminal, and press Enter.
3. Run:

```bash
bash Start-IP-Tracker.command
```

Do not put `cd` before `bash`. The launcher looks for Python 3.11 or newer.
Use `python3 --version` to check your default version. If needed, install Python
from https://www.python.org/downloads/ and reopen Terminal.

## Windows

Install Python 3.11 or newer with **Add Python to PATH** enabled. Extract the ZIP
and double-click **Start-IP-Tracker.bat**.

## Linux

Open Terminal in the extracted folder and run `sh start-ip-tracker.sh`.
Your distribution may require its `python3-venv` package.

## After launch

- **My device:** select your Wi-Fi, Ethernet or VPN adapter to view local addresses.
- **Detect public IPs:** check the internet-facing IPv4 and IPv6 addresses.
- **IP lookup:** enter an IPv4 or IPv6 address to view network details.
- **3D map:** appears after a lookup returns coordinates. Drag to move, scroll to zoom, or Ctrl + drag to rotate/tilt. Use **Globe view**, **Recenter**, or **2D / 3D**. Google Maps and satellite links open separately. The marker is approximate, not GPS.
- **Lookup history:** export results to CSV.

The package requires Python 3.11+ and Internet on first launch to install dependencies.
Local device addresses work offline after setup. Public detection and geolocation need Internet.

Keep the Terminal window open while using the app. Press **Ctrl+C** to stop it.
Run the same launcher next time. The app uses port **8502**, so NetCheck can still use **8501**.

## If something goes wrong

- **No such file or directory:** you are in the wrong folder. The launcher is beside `app.py`; type `ls` on Mac to check the files.
- **Python too old:** install Python 3.11 or newer and reopen Terminal.
- **Setup/download error:** check Internet access and retry the launcher.
- **Port already in use:** close the other IP Tracker terminal window or stop it with Ctrl+C.
- **Moved folder or upgraded Python:** stop the app, delete only this project's `.venv` folder and restart the launcher.
- **MAC not reported:** the OS may not expose a link-layer address for that adapter; select another adapter.
- **IPv6 not detected:** IPv6 connectivity or the provider may be unavailable. IPv4 and local checks remain usable.

See README.md for full documentation and LICENSE for the MIT license.
