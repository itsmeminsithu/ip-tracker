# Validation

## Passed

- 54 automated tests on Linux with Python 3.12.
- Tests cover IP validation and classification, IPv4/IPv6 separation, local adapter data, MAC handling, private-IP request exclusion, provider failures, CSV escaping, coordinate validation, generated globe HTML and Streamlit dashboard interactions.
- First-run setup completed in a fresh virtual environment.
- Setup dependency-import check passed.
- Streamlit server started in that environment and its HTTP health endpoint returned `ok`.
- macOS/Linux launcher syntax and Python source compilation passed.
- Generated globe JavaScript passed Node.js syntax validation.

## Limits

- Real interface enumeration was blocked by this execution environment's OS permissions. Adapter rendering was tested with representative fixture data. The app displays an error if the OS denies access.
- A live public lookup timed out in this environment. Provider success and failure responses were tested with fixtures; no live lookup success is claimed.
- The Cesium CDN script was reachable, but a browser installation failed, so WebGL rendering and map controls have not been visually verified here.
- macOS and Windows launchers have not been executed on those systems.
- The included GitHub Actions matrix has not yet run on GitHub.

Run `python -m pytest -q` from the project folder after installing requirements-dev.txt.
