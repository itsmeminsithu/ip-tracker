# Upload to GitHub

Repository name: `ip-tracker`

Description:
> A Python dashboard for IPv4, IPv6 and MAC addresses, public IP detection, IP lookup and an interactive 3D globe. Built by Min SiThu (devminsithu).

## Recommended: Git from your Mac

1. Extract `IP-Tracker-GitHub.zip`.
2. Create an empty repository named `ip-tracker` under `devminsithu` on GitHub. Do not add a README, license or gitignore during creation; they are included here.
3. Open Terminal, type `cd ` with a space, drag the extracted `ip-tracker` folder into Terminal, and press Enter.
4. Run these commands one at a time:

```bash
git init -b main
git add .
git status --short
git commit -m "Initial release of IP Tracker"
git remote add origin https://github.com/devminsithu/ip-tracker.git
git push -u origin main
```

Review `git status` before committing. Installed dependencies, caches and default data exports are excluded by `.gitignore`. Use your normal GitHub authentication when prompted. Do not put passwords or access tokens in source files.

If Git asks for your identity, configure it for this repository:

```bash
git config user.name "Min SiThu"
git config user.email "YOUR_VERIFIED_GITHUB_EMAIL_OR_NOREPLY_ADDRESS"
```

Replace the email placeholder with your actual GitHub commit email, then rerun the commit and push commands.

## Browser upload

Extract the ZIP first. Upload the **contents** of the `ip-tracker` folder so that `README.md`, `app.py` and `LICENSE` are at the repository root. Uploading only the ZIP does not create a usable source repository.

Include these folders and files that Finder normally hides:

- `.github/workflows/tests.yml`
- `.streamlit/config.toml`
- `.gitignore`

On Mac, press **Command + Shift + .** in Finder to reveal hidden items. Git upload is recommended because it preserves all files and executable permissions.

## After uploading

Check that README.md appears on the repository homepage, the MIT license is detected, and the tests workflow runs. The package includes all source code, launchers, tests and documentation. It does not contain a pre-created remote repository or Git history.
