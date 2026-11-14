# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import urllib.request

PLUGIN_PY_URL = "https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/plugin.py"
ICONS_BASE = "https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/"
SCRIPTS_JSON = "data/scripts.json"
ICONS_DIR = "LSicons2"
PLUGIN_PY = "plugin.py"
SKINS_DIR = "skins"

# Icone che NON devono essere mai cancellate
KEEP_ALWAYS = {
    "LSS.png", "Blank.png", "Information.png", "about.png", "Github.png",
    "script.png", "Backup.png", "Bouquets.png", "Channel-list.png",
    "ciefp.png", "Game.png", "KiddaC1.png", "KiddaC2.png",
    "lululla_script.png", "oe2.0.png", "oe2.5-2.6.png",
    "OE2.2-Plugins.png", "OE2.2-Skins.png",
    "Feeds2.0.png", "Feeds2.2.png", "SOE20.png", "SOE22.png",
    "skinsteam.png", "otherskins.png", "SkinHD.png", "egami.png",
    "hdf.png", "openbh.png", "openatv.png", "openpli.png", "openspa.png",
    "vti.png", "oebased.png", "iptv-streaming.png", "mediayou.png",
    "multiboot.png", "Multimedia.png", "Panels.png", "picons.png",
    "Library.png", "Radio.png", "key-updater.png", "key-updater1.png",
    "sport.png", "streamlink.png", "utility.png", "vpn.png",
    "weather.png", "weather-forecast.png", "webcam.png",
    "18+.png", "18+deb.png", "Other.png", "Other1.png",
    "cyrus.png", "manutek.png", "morpheus883.png",
    "vhannibal1.png", "vhannibal2.png", "LcnSearch.png",
    "CheckSkin.png", "cccamfreee.png", "oscamfree.png",
    "usb-tuner-drivers.png", "plugin-epg.png",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def parse_plugin_list(text):
    m = re.search(r"PLUGIN_LIST\s*=\s*\[(.*?)\]", text, re.DOTALL)
    if not m:
        raise RuntimeError("PLUGIN_LIST non trovato in plugin.py")
    block = m.group(1)
    tuple_re = re.compile(
        r'\(\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*\)',
        re.DOTALL)
    items = []
    for match in tuple_re.finditer(block):
        name, icon_path, cmd, pkg1, pkg2 = match.groups()
        cmd = cmd.replace('--no-check-certificate ', '')
        items.append({
            "name": name.strip(),
            "icon_file": os.path.basename(icon_path.strip()),
            "cmd": cmd.strip()
        })
    return items


def download_icon(icon_file):
    dest = os.path.join(ICONS_DIR, icon_file)
    if os.path.exists(dest):
        return icon_file

    url = ICONS_BASE + icon_file
    try:
        data = fetch(url)
        with open(dest, "wb") as f:
            f.write(data)
        print("  [icon] " + icon_file + " (" + str(len(data)) + " bytes)")
    except Exception as e:
        print("  [ERR]  " + icon_file + ": " + str(e))
    return icon_file


def collect_referenced():
    refs = set(KEEP_ALWAYS)
    if os.path.exists(SCRIPTS_JSON):
        with open(SCRIPTS_JSON, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for cat, items in cfg.get("categories", {}).items():
            for it in items:
                if it.get("icon"):
                    refs.add(it["icon"])
    if os.path.exists(PLUGIN_PY):
        with open(PLUGIN_PY, "r", encoding="utf-8") as f:
            py = f.read()
        for m in re.finditer(r'"([A-Za-z0-9_\-\.+]+\.png)"', py):
            refs.add(m.group(1))
    if os.path.isdir(SKINS_DIR):
        for root, _, files in os.walk(SKINS_DIR):
            for fn in files:
                if fn.endswith(".xml"):
                    with open(os.path.join(root, fn), "r", encoding="utf-8", errors="replace") as f:
                        for m in re.finditer(
                                r'/LSicons2/([A-Za-z0-9_\-\.+]+\.png)', f.read()):
                            refs.add(m.group(1))
    return refs


def main():
    print("1) Scarico plugin.py di Ciefp...")
    try:
        raw = fetch(PLUGIN_PY_URL).decode("utf-8", errors="replace")
        items = parse_plugin_list(raw)
    except Exception as e:
        print("   ERRORE: " + str(e))
        return 1

    if len(items) < 20:
        print("   ERRORE: trovati solo " +
              str(len(items)) + " plugin. Formato cambiato?")
        return 1

    print("   trovati " + str(len(items)) + " plugin")

    print("2) Scarico icone mancanti...")
    new_entries = []
    for it in items:
        real_icon_name = download_icon(it["icon_file"])
        new_entries.append({
            "name": it["name"],
            "icon": real_icon_name,
            "cmd": it["cmd"]
        })

    print("3) Aggiorno data/scripts.json...")

    # Se il JSON non esiste, non lo creiamo da zero qui.
    # Assumiamo che tu lo abbia già pushato con LulullaScript e Script
    # Installer.
    if not os.path.exists(SCRIPTS_JSON):
        print("   ERRORE: data/scripts.json non trovato. Assicurati di averlo pushato.")
        return 1

    try:
        with open(SCRIPTS_JSON, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print("   ERRORE: impossibile leggere il JSON: " + str(e))
        return 1

    if cfg.get("categories", {}).get("Ciefp") != new_entries:
        cfg.setdefault("categories", {})["Ciefp"] = new_entries
        cfg["updated"] = "auto-sync"

        with open(SCRIPTS_JSON, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("   JSON aggiornato con successo.")
    else:
        print("   JSON già aggiornato (nessuna modifica).")

    print("4) Pulisco icone orfane in LSicons2/...")
    refs = collect_referenced()
    if len(refs) < 50:
        print("   ERRORE: troppi pochi riferimenti trovati. Salto la pulizia.")
        return 1

    deleted = 0
    for fn in os.listdir(ICONS_DIR):
        if fn.lower().endswith(".png") and fn not in refs:
            os.remove(os.path.join(ICONS_DIR, fn))
            deleted += 1

    if deleted > 0:
        print("   Cancellate " + str(deleted) + " icone orfane.")
    else:
        print("   Nessuna icona orfana da cancellare.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
