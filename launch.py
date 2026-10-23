#!/usr/bin/env python3
"""Set up and start IP Tracker. Copyright (c) 2026 Min SiThu (devminsithu).
SPDX-License-Identifier: MIT
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
ENV = ROOT / '.venv'
PYTHON = ENV / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
MARKER = ENV / '.iptracker-requirements'


def main():
    if sys.version_info < (3, 11):
        print('IP Tracker requires Python 3.11 or newer. Install it from https://www.python.org/downloads/')
        return 1
    os.chdir(ROOT)
    print('IP Tracker — Min SiThu (devminsithu)', flush=True)
    if not PYTHON.exists():
        print('First run: creating a private Python environment…', flush=True)
        venv.EnvBuilder(with_pip=True).create(ENV)
    fingerprint = hashlib.sha256((ROOT / 'requirements.txt').read_bytes()).hexdigest()
    previous = MARKER.read_text().strip() if MARKER.exists() else ''
    if previous != fingerprint:
        print('Installing dependencies. Internet is required for this step…', flush=True)
        subprocess.run([str(PYTHON), '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')], check=True)
        MARKER.write_text(fingerprint)
    if '--check' in sys.argv:
        subprocess.run([str(PYTHON), '-c', 'import streamlit, psutil, requests; print("Setup is ready.")'], check=True)
        return 0
    print('Opening IP Tracker at http://127.0.0.1:8502', flush=True)
    print('Keep this window open. Press Ctrl+C to stop.', flush=True)
    return subprocess.call([str(PYTHON), '-m', 'streamlit', 'run', str(ROOT / 'app.py'),
                            '--server.address=127.0.0.1', '--server.port=8502',
                            '--server.headless=false', '--browser.gatherUsageStats=false'])


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('\nIP Tracker stopped.')
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f'Could not start IP Tracker: {exc}', file=sys.stderr)
        print('See QUICKSTART.md. Check Python, your Internet connection and folder write permissions.', file=sys.stderr)
        raise SystemExit(1)
