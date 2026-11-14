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

DEFAULT_JSON = {
    "schema": 1,
    "updated": "auto-sync",
    "min_plugin_version": "3.0.7",
    "categories": {
        "LulullaScript": [
            {"name": "Acherone Script Command", "icon": "acherone_script_command.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/acherone-script/main/installer.sh -O - | /bin/sh"},
            {"name": "Advanced Screeshots", "icon": "advanced_screeshots.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/AdvancedScreenshot/main/installer.sh -O - | /bin/sh"},
            {"name": "Apod", "icon": "apod.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/apod/main/installer.sh -O - | /bin/sh"},
            {"name": "Apsattv", "icon": "apsat.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/Apsattv/main/installer.sh -O - | /bin/sh"},
            {"name": "Archimede M3u Converter", "icon": "archimede_m3u_converter.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/Archimede-M3UConverter/main/installer.sh -O - | /bin/sh"},
            {"name": "Calendar", "icon": "calendar.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/Calendar/main/installer.sh -O - | /bin/sh"},
            {"name": "DDRSS Reader", "icon": "ddrss.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/DDRSSReader/main/installer.sh -O - | /bin/sh"},
            {"name": "EPGImport 99", "icon": "epgimport_99.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/EPGImport-99/main/installer_source.sh -O - | /bin/bash"},
            {"name": "EPGImport Source", "icon": "epgsource.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/EPGImport-99/main/installer_source.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Filmon", "icon": "filmon.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/Filmon/main/installer.sh -O - | /bin/sh"},
            {"name": "ForecaOne", "icon": "ForecaOne.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/ForecaOne/main/installer.sh -O - | /bin/sh"},
            {"name": "Freearhey", "icon": "freearhey.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/freearhey/main/installer.sh -O - | /bin/sh"},
            {"name": "HasBahCa", "icon": "hasbahca.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/HasBahCa/main/installer.sh -O - | /bin/sh"},
            {"name": "Horoscope", "icon": "horoscope.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/Horoscope/main/installer.sh -O - | /bin/sh"},
            {"name": "mmPicons", "icon": "mmpicons.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/mmPicons/main/installer.sh -O - | /bin/sh"},
            {"name": "Oroscopo Italia", "icon": "oroscopoitalia.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/oroscopo_radioitalia/main/installer.sh -O - | /bin/sh"},
            {"name": "Parsa Tv", "icon": "parsatv.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/tvParsa/main/installer.sh -O - | /bin/sh"},
            {"name": "Radio80", "icon": "radio80.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/Radio-80-s/main/installer.sh -O - | /bin/sh"},
            {"name": "Radio Git", "icon": "radio_git.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/RadioGit/main/installer.sh -O - | /bin/sh"},
            {"name": "Rai Play", "icon": "rai_play.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/RaiPlay/main/installer.sh -O - | /bin/sh"},
            {"name": "Rsi Live", "icon": "rsilive.png", "cmd": "wget -q https://raw.githubusercontent.com/OwnerPlugins/rsilive/main/installer.sh -O - | /bin/bash"},
            {"name": "Rss Reader", "icon": "rss_reader.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/RSSReader/main/installer.sh -O - | /bin/sh"},
            {"name": "Scsearch", "icon": "scsearch.png", "cmd": "wget -q https://raw.githubusercontent.com/OwnerPlugins/scsearch/main/installer.sh -O - | /bin/bash"},
            {"name": "StreamProxy", "icon": "streamproxy.png", "cmd": "wget -q https://raw.githubusercontent.com/OwnerPlugins/StreamProxy/main/installer.sh -O - | /bin/bash"},
            {"name": "SlWebcams", "icon": "slwebcams.png", "cmd": "wget -q https://raw.githubusercontent.com/OwnerPlugins/SLwebcams/main/installer.sh -O - | /bin/bash"},
            {"name": "Softcam Manager", "icon": "softcam_manager.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/tvManager/main/installer.sh -O - | /bin/sh"},
            {"name": "Stalker Portal Converter", "icon": "stalker_portal_converter.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/StalkerPortalConverter/main/installer.sh -O - | /bin/sh"},
            {"name": "Stvcl", "icon": "stvcl.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/S.T.V.C.L-/main/installer.sh -O - | /bin/sh"},
            {"name": "TvDream", "icon": "tvdream.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/tvDream/main/installer.sh -O - | /bin/sh"},
            {"name": "TVGarden", "icon": "tvgarden.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/installer.sh\" -O - | /bin/sh"},
            {"name": "TvSettings", "icon": "tvsettings.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/tvSettings/main/installer.sh -O - | /bin/sh"},
            {"name": "TvToM3u", "icon": "tvtom3u.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/TvToM3u/main/installer.sh -O - | /bin/sh"},
            {"name": "Vavoo", "icon": "vavoo.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/vavoo/main/installer.sh -O - | /bin/sh"},
            {"name": "WiFi Manager", "icon": "wifi_manager.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/WiFi-Manager/main/installer.sh -O - | /bin/sh"},
            {"name": "Worldcam", "icon": "worldcam.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/WorldCam/main/installer.sh -O - | /bin/sh"},
            {"name": "XC Forever", "icon": "xc.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/xc_plugin_forever/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "XXX Plugin", "icon": "xxx_plugin.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/xxxplugin/main/installer.sh -O - | /bin/sh"}
        ],
        "Ciefp": [],
        "Script Installer": [
            {"name": "Add Libssl Libcrypto", "icon": "AddLibssl.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Add_Libssl1_Libcrypto1.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Add Symlink Libssl", "icon": "AddSymlink.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Symlink_Creator.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Ajpanel AMAJamry", "icon": "Ajpanel.png", "cmd": "wget \"https://raw.githubusercontent.com/biko-73/AjPanel/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Arabic Savior", "icon": "arabicsav.png", "cmd": "wget \"https://raw.githubusercontent.com/fairbird/ArabicSavior/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Biss Feed Autokey", "icon": "BissFeedAutokey.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Bissfeedautokey.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Chocholousek Picons", "icon": "ChocholousekPicons.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Chocholousek_picons.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Dns Cloudfaire", "icon": "DnsCloudfaire.png", "keep_open": True, "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/DnsCloudflare.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Dns Google", "icon": "DnsGoogle.png", "keep_open": True, "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/DnsGoogle.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Dns Quad9", "icon": "DnsQuad9.png", "keep_open": True, "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/DnsQuad9.sh?inline=false\" -O - | /bin/sh"},
            {"name": "E2player E2-MIRROR", "icon": "E2iPlayer.png", "cmd": "wget -q \"https://raw.githubusercontent.com/oe-mirrors/e2iplayer/refs/heads/python3/e2iplayer_install.sh?inline=false\" -O - | /bin/sh"},
            {"name": "E2player BYKO-73", "icon": "E2playerBiko-73.png", "cmd": "wget -q \"https://raw.githubusercontent.com/biko-73/E2IPlayer/main/installer-tar.sh?inline=false\" -O - | /bin/sh"},
            {"name": "E2player MAXBAMBY", "icon": "E2playerMAXBAMBY.png", "cmd": "wget -q \"https://gitlab.com/maxbambi/e2iplayer/-/raw/master/install-e2iplayer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "E2player ZADMARIO", "icon": "E2playerZADMARIO.png", "cmd": "wget -q \"https://gitlab.com/zadmario/e2iplayer/-/raw/master/install-e2iplayer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "EPGImport - source", "icon": "epgsource.png", "keep_open": True, "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/EPGImport-99/main/installer_source.sh?inline=false\" -O - | /bin/sh"},
            {"name": "History Zap Selector", "icon": "HistoryZapSelector.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Historyzapselector_dorik.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Ipaudio Pro", "icon": "ipaudio.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Ipaudiopro_1.4.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Keys Adder", "icon": "keysadd.png", "keep_open": True, "cmd": "wget -q \"https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Keys Update", "icon": "keys.png", "keep_open": True, "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Keys_Updater.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Levi45 Manager", "icon": "Levi45Manager.png", "cmd": "wget -q \"https://raw.githubusercontent.com/levi-45/Manager/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Linuxsat Addons Panel", "icon": "Linuxsat.png", "cmd": "wget -q https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/installer.sh -O - | /bin/sh"},
            {"name": "Mountpoints", "icon": "Mountpoints.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Mountpoints.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Multistalker Pro Ziko", "icon": "MultistalkerPro.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/refs/heads/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/multisalker_pro12_eliesat.sh?inline=false\" -O - | /bin/sh;wget -q \"https://gitlab.com/hmeng80/extensions/-/raw/main/multistalker/portal/Portal_multistalker.sh?inline=false\" -O - | /bin/sh"},
            {"name": "New VirtualKeyboard", "icon": "NewVirtualKeyboard.png", "cmd": "wget -q \"https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Oscam Generator LINGSAT", "icon": "lingsat.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Oscam_srvid_generator_lyngsat.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Oscam Generator KINGOFSAT", "icon": "kingofsat.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Oscam_srvid_generator_kingofsat.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Oscam Generator SATELINATV", "icon": "satelinatv.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Oscam_srvid_generator_satelitnatv.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Oscam Generator TWOJEIP", "icon": "twojeip.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Oscam_srvid_generator_twojeip.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Quicksignal Raed", "icon": "Quicksignal.png", "cmd": "wget -q \"https://raw.githubusercontent.com/fairbird/RaedQuickSignal/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "WireGuard Vpn", "icon": "WireGuard.png", "cmd": "wget -qO- \"https://raw.githubusercontent.com/m4dhouse/Wireguard-Vpn/python-3.12/WireGuard.sh\" -O -  | /bin/sh"},
            {"name": "Xstreamity", "icon": "xstreamity.png", "cmd": "wget -q \"https://raw.githubusercontent.com/biko-73/xstreamity/main/installer.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Xtraevent", "icon": "xtraevent.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Xtraevent.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Lcn Scanner", "icon": "LcnSearch.png", "action": "lcn"},
            {"name": "Check Skin Conponent", "icon": "CheckSkin.png", "action": "checkskin"},
            {"name": "Send Cline -> CCcam.cfg", "icon": "cccamfreee.png", "action": "cline_cccam"},
            {"name": "Send Cline -> oscam.server", "icon": "oscamfree.png", "action": "cline_oscam"},
            {"name": "Send Emm", "icon": "SendEmm.png", "keep_open": True, "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Emm_Sender.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Subsupport addon", "icon": "SubSupportAddon.png", "cmd": "wget -q \"https://raw.githubusercontent.com/Belfagor2005/LinuxsatPanel/main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/sh/Subsupport_addon.sh?inline=false\" -O - | /bin/sh"},
            {"name": "Transmission addon", "icon": "transmission.png", "cmd": "wget -q \"https://dreambox4u.com/dreamarabia/Transmission_e2/Transmission_e2.sh?inline=false\" -O - | /bin/sh"},
            {"name": "ServiceApp Exteplayer", "icon": "serviceapp.png", "cmd": "opkg update && opkg --force-reinstall --force-overwrite install ffmpeg gstplayer exteplayer3 enigma2-plugin-systemplugins-serviceapp"}
        ]
    }
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
        return
    url = ICONS_BASE + icon_file
    try:
        data = fetch(url)
        with open(dest, "wb") as f:
            f.write(data)
        print(f"  [icon] {icon_file} ({len(data)} bytes)")
    except Exception as e:
        print(f"  [ERR]  {icon_file}: {e}")


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
        print(f"   ERRORE: {e}")
        return 1

    if len(items) < 20:
        print(
            f"   ERRORE: trovati solo {
                len(items)} plugin. Formato cambiato?")
        return 1

    print(f"   trovati {len(items)} plugin")

    print("2) Scarico icone mancanti...")
    for it in items:
        download_icon(it["icon_file"])

    print("3) Aggiorno data/scripts.json...")

    cfg = DEFAULT_JSON
    if os.path.exists(SCRIPTS_JSON):
        try:
            with open(SCRIPTS_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass

    new_entries = [{"name": it["name"],
                    "icon": it["icon_file"],
                    "cmd": it["cmd"]} for it in items]

    if cfg.get("categories", {}).get("Ciefp") != new_entries:
        cfg.setdefault("categories", {})["Ciefp"] = new_entries
        cfg["updated"] = "auto-sync"

        os.makedirs(os.path.dirname(SCRIPTS_JSON), exist_ok=True)
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
        print(f"   Cancellate {deleted} icone orfane.")
    else:
        print("   Nessuna icona orfana da cancellare.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
