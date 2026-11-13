<h1 align="center">📡 Linuxsat-Support Panel Addons</h1>

<p align="center">
  <a href="https://github.com/Belfagor2005/LinuxsatPanel">
    <img src="https://img.shields.io/badge/Version-3.0.7-blue.svg" alt="Version">
  </a>

  <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">
    <img src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-green.svg" alt="License">
  </a>

  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-2.7%2F3.x-yellow.svg" alt="Python">
  </a>

  <a href="https://github.com/Belfagor2005/LinuxsatPanel/actions/workflows/pylint.yml">
    <img src="https://github.com/Belfagor2005/LinuxsatPanel/actions/workflows/pylint.yml/badge.svg" alt="Python package">
  </a>
</p>

<p align="center">
  <a href="https://github.com/Belfagor2005">
    <img src="https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet" alt="Visitors">
  </a>
</p>

<p align="center">
  <a href="https://ko-fi.com/lululla">
    <img src="https://img.shields.io/badge/_-Donate-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge" alt="Ko-fi">
  </a>

  <a href="https://paypal.me/belfagor2005">
    <img src="https://img.shields.io/badge/_-Donate-green.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge" alt="PayPal">
  </a>
</p>

---

<p align="center">
  <img src="https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/LinuxsatPanel.png" alt="Linuxsat Panel">
</p>

---

## 📌 About

**Linuxsat-Support Panel** is a professional addons manager for Enigma2-based satellite receivers.

- 🐧 Supports: OE2.0 (ipkg) | OE2.2/2.5/2.6 (dpkg)
- 🖥️ Resolutions: HD | FHD | WQHD
- 📡 33+ categories | 40+ community scripts | 100+ plugins
- 🗂️ **JSON-driven script catalog** — add new scripts without releasing a new plugin build

---

## 🗓️ Version History

### v3.0.7 (Current)

**New**
- 🆕 **JSON-based script configuration** — `LulullaScript`, `Ciefp` and `Script Installer` now read their entry lists from `data/scripts.json` (remote with local fallback). Add, remove or reorder scripts **without releasing a new plugin build**.
- 🆕 Background preload of `scripts.json` at plugin startup — first category access is instant, no UI freeze.
- 🆕 Graceful error message when `scripts.json` is missing or invalid.
- 🆕 `keep_open` flag per script (replaces fragile keyword matching for interactive scripts like DNS changers).

**Fixes**
- ✅ Removed broken "view log?" popup after script execution (console closed without returning a result, log file was never written).
- ✅ Removed dead `_view_log`, `file_log`, and orphan `File_Commander` import path.
- ✅ `addInstall` → **Remove** now uses `dpkg -r` on DreamOS/OE2.2+ (was always calling `opkg remove`, silently failing).
- ✅ Fixed 2 case-sensitive icon references in `scripts.json` (`ciefpkingsat.png`, `titlovibrowser.png` — Linux filesystems are case-sensitive).
- ✅ Removed dead `LcnXX` / `_onLCNScanFinished` methods from `addInstall`.
- ✅ Fixed memory leak in splash screen (`ePicLoad` now released after use).
- ✅ Fixed `startLP` logo path (`icons/pageLogo.png` → `icons2/Logo.png`, the old path never existed).
- ✅ `checkGZIP` now catches generic `Exception` (previously crashed with `NameError` if `requests` wasn't installed).
- ✅ `check_and_install_requests` made idempotent (runs once per boot via `/tmp` marker, no repeated `opkg update`).

**Cleanup**
- 🧹 Ruff lint clean — removed unused imports (`time`, `getmtime`, `LCNScanner`), redundant `int()` calls, module-level `global` statements.
- 🧹 Regenerated `.po` translation sources (12-24 MB → ~20 KB per file, from `.pot` + `.mo`).
- 🧹 Removed 26 orphan PNGs from `LSicons2/` (~600 KB).
- 🧹 IPK build excludes `.po` sources, `ruff.toml`, `translate_utils.py`, `update_translations.py`, `translation_cache.json`, `commits_cache.json`.

### v3.0.6
- Security: removed `--no-check-certificate` from every wget install/update call
- Hardened `lsConsole` and `checkskin` temp files against local symlink attacks
- Fixed LCN scan (Order LCN Bouquet) always logging a false error even on success
- Fixed possible crash/misfile reading lcndb entries with an unexpected mode
- Fixed commits cache never actually loading (str repr vs JSON mismatch)
- Fixed crash risk in RTL/Arabic font loading (`add_skin_fonts`)
- Removed unused `translate_utils.py` and duplicate code

### v3.0.5
- Added Commit History viewer (INFO button → Commit History)
- `LSinfo` now supports 3 modes: info/about/commits
- Commit list shows date, author, message and hash
- Added cache system for commits (saves to `commits_cache.json`)
- Auto-refresh cache every 24 hours
- Rate limit handling with fallback to cached data
- Updated `info.txt` with clean formatting (no special chars)
- Fixed `AsyncMixin` inheritance for `LSinfo`
- Fixed console output for script execution (removed redirections)

### v3.0.4
- Added Commit History viewer via GitHub API
- Improved `LSinfo` screen with multi-mode support (info/about/commits)
- Removed decorative ASCII lines for better compatibility
- Updated `info.txt` with clean formatting
- Fixed `AsyncMixin` inheritance for `LSinfo`

### v3.0.3
- General fixes and improvements

### v3.0.2
- Script Installer: remote scripts (wget/opkg entries) fixed
- Local scripts from `sh/` folder now listed alphabetically
- File Commander: button labels translated again

### v3.0.1
- Bump to 3.0.1; responsive File Commander UI
- Refactor script installer to dynamically load shell scripts
- Apply auto PEP8 aggressive fixes

### v3.0.0
- Search all addons with green button
- Installed addons shown in green
- No more GUI freezes (async downloads, catalog cache)
- Safe settings install with automatic backup
- Update check on panel start
- Big cleanup and many bugfixes

> Older versions: see [GitHub Releases](https://github.com/Belfagor2005/LinuxsatPanel/releases)

---

## 👥 Credits

**Suggested by:**
- @masterG
- @oktus
- @pcd

**Maintainer:**
- All code rewritten by **Lululla** (since 2024.07.20)
- Thanks to @pQu4k3r for support

**Designs & Graphics:**
- @oktus

---

## 🛠️ Features

- ✅ One-click installation of plugins, skins & scripts
- ✅ Automatic detection of package manager (opkg/dpkg)
- ✅ Free C-line integration (CCcam & Oscam)
- ✅ LCN Scanner for terrestrial channel ordering
- ✅ Script Installer with 40+ community scripts
- ✅ Ciefp specialized installer
- ✅ Live console output during installations
- ✅ Integrated File Commander for logs
- ✅ Automatic update notifications
- ✅ **JSON-driven script catalog** — update the addon list without releasing a plugin update
- ✅ Commit History viewer (via GitHub API with cache)

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| Arrow keys | Navigate through the grid |
| OK | Open selected category/execute action |
| RED | Exit to About screen |
| GREEN | Search addons |
| YELLOW (long press) | Force update |
| BLUE | Restart Enigma2 GUI |
| INFO | Show system information / Commit History |
| 0 (ZERO) | Toggle A-Z/Default sorting |

---

## 📚 Categories

| Category | Category | Category |
|----------|----------|----------|
| Backup Tools | Bouquets Tools | Channel List |
| Ciefp Installer | DvbUsb Drivers | EPG Tools |
| Feeds Image | Games Tools | IPTV Tools |
| KiddaC | Lululla Scripts | Lululla Zone |
| Mediaplayer-Youtube | MultiBoot Tools | Multimedia Tools |
| Panels Addons | Picons Tools | Python Library |
| Radio Tools | Script Installer | Skins Team |
| Keys Tools | Softcams | Sport Tools |
| Streamlink Tools | Utility Tools | VPN Tools |
| WeatherTools | WeatherForecast | Webcam Tools |
| Adult (18+) | Other | Information |
| About | | |

---

## 🔧 Script Catalog (`data/scripts.json`)

All script lists (`LulullaScript`, `Ciefp`, `Script Installer`) are loaded at runtime from `data/scripts.json`.

**To add a new script, you don't need to touch the Python code** — just edit the JSON file and either:

1. **Rebuild the plugin** — the bundled `data/scripts.json` is loaded as local fallback.
2. **Update the remote file** — push changes to:
   ```
   https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/data/scripts.json
   ```
   All existing installations will see the new entry within one hour (cached in memory, then refreshed).

### JSON schema

```json
{
  "schema": 1,
  "updated": "2025-11-13",
  "min_plugin_version": "3.0.6",
  "categories": {
    "Script Installer": [
      {
        "name": "My Script",
        "icon": "script.png",
        "cmd": "wget -q https://example.com/installer.sh -O - | /bin/sh",
        "keep_open": false
      }
    ],
    "LulullaScript": [
      {
        "name": "Acherone Script Command",
        "icon": "acherone_script_command.png",
        "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/acherone-script/main/installer.sh -O - | /bin/sh"
      }
    ],
    "Ciefp": [
      {
        "name": "CiefpBouquetUpdater",
        "icon": "ciefp_bu.png",
        "cmd": "wget -q https://raw.githubusercontent.com/ciefp/CiefpBouquetUpdater/main/installer.sh -O - | /bin/sh"
      }
    ]
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Display name in the grid |
| `icon` | yes | PNG filename in `LSicons2/` (case-sensitive on Linux) |
| `cmd` | yes* | Shell command to execute |
| `action` | yes* | Internal action key (`lcn`, `checkskin`, `cline_cccam`, `cline_oscam`) — alternative to `cmd` |
| `keep_open` | no | If `true`, the console stays open (for interactive scripts) |

\* exactly one of `cmd` or `action` per entry.

### Fallback chain

1. Remote URL (cached in memory for 1 hour, fetched once per session)
2. Local `data/scripts.json` (always fresh, read on every category open)
3. In-memory stale cache (if remote failed and local missing)
4. Error message + close screen (if all fail)

### Preload

At plugin startup (`Plugins()` in `plugin.py`), a background thread preloads `scripts.json` so the first category access is instant. No UI freeze on slow networks.

---

## 📸 Screenshots

![Screenshot](https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/screenshot/1.png)

---

## ⚠️ License

This is free software; you can redistribute it and/or modify it under the terms of the **GNU General Public License** as published by the **Free Software Foundation**; either version 2, or (at your option) any later version.

You **must not** remove the credits at all, and you **must** make the modified code open to everyone.

---

## 💳 Donations

The plugin lives thanks to donations from users like you!

- ☕ [Ko-fi](https://ko-fi.com/lululla)
- 💰 [PayPal](https://paypal.me/belfagor2005)

---

## 🔗 Links

- **Support:** [linuxsat-support.com](https://linuxsat-support.com)
- **Repository:** [GitHub](https://github.com/Belfagor2005/LinuxsatPanel)
- **Commit History:** [OwnerPlugins/upload](https://github.com/OwnerPlugins/upload)
- **Script Catalog:** [data/scripts.json](https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/data/scripts.json)

---

<p align="center">
  <strong>Made with ❤️ by Lululla</strong>
</p>
