#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from Components.Language import language
from Tools.Directories import (resolveFilename, SCOPE_PLUGINS)
from enigma import (
    RT_HALIGN_RIGHT,
    RT_HALIGN_LEFT,
    getDesktop,
)
from os.path import exists, dirname, join
from os import popen, environ, statvfs, system
import gettext
import sys

__author__ = "Lululla"
__email__ = "ekekaz@gmail.com"
__copyright__ = 'Copyright (c) 2024 Lululla'
__license__ = "GPL-v2"
__version__ = "3.0.7"


# ─── JSON scripts config ─────────────────────────────────────────────
# URL remoto (produzione). Per test locale il loader fa fallback al
# file locale se il remoto non risponde (404 = non ancora pubblicato).
SCRIPTS_JSON_URL = (
    "https://raw.githubusercontent.com/OwnerPlugins/LinuxsatPanel/"
    "main/usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/data/scripts.json?v=3.0.8"
)
# Fallback locale: data/scripts.json dentro il plugin.
SCRIPTS_JSON_LOCAL = "Extensions/LinuxsatPanel/data/scripts.json"

_scripts_cfg = {
    "data": None,
    "time": 0,
    "remote_tried": False,
    "remote_failed": False,
}
SCRIPTS_CFG_TTL = 3600  # secondi di cache per il remoto (1h)


def get_scripts_config(force=False):
    import time
    import json as _json
    from os import makedirs

    now = time.time()
    try:
        local_path = resolveFilename(SCOPE_PLUGINS, SCRIPTS_JSON_LOCAL)
    except Exception:
        local_path = join(dirname(__file__), "data", "scripts.json")

    # 1) Cache in memoria (solo se NON stiamo forzando)
    if not force and _scripts_cfg["data"] is not None:
        if now - _scripts_cfg["time"] < SCRIPTS_CFG_TTL:
            return _scripts_cfg["data"]

    # 2) Tentativo remoto (o forzato)
    if force or not _scripts_cfg["remote_tried"]:
        _scripts_cfg["remote_tried"] = True
        try:
            req = Request(SCRIPTS_JSON_URL, headers={
                "User-Agent": AgentRequest,
                "Cache-Control": "no-cache",
            })
            with urlopen(req, timeout=10) as resp:
                if resp.getcode() == 200:
                    raw_data = resp.read().decode("utf-8")
                    data = _json.loads(raw_data)
                    _scripts_cfg["data"] = data
                    _scripts_cfg["time"] = now
                    print("[scripts.json] loaded from remote")
                    
                    # --- AGGIUNTA FONDAMENTALE: Salva sul box! ---
                    try:
                        makedirs(dirname(local_path), exist_ok=True)
                        with open(local_path, "w", encoding="utf-8") as f:
                            f.write(raw_data)
                        print("[scripts.json] file locale aggiornato dal remoto")
                    except Exception as e:
                        print("[scripts.json] errore salvataggio locale:", e)
                    # ---------------------------------------------
                    
                    return data
                else:
                    print("[scripts.json] remote HTTP %d" % resp.getcode())
        except Exception as e:
            print("[scripts.json] remote failed:", e)
        _scripts_cfg["remote_failed"] = True

    # 3) Fallback locale
    if exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                data = _json.load(f)
            print("[scripts.json] loaded from local:", local_path)
            return data
        except Exception as e:
            print("[scripts.json] local failed:", e)

    # 4) Ultima spiaggia
    if _scripts_cfg["data"] is not None:
        print("[scripts.json] using stale cache")
        return _scripts_cfg["data"]

    return None


# ─── Requests auto-install (idempotente) ────────────────────────────
def check_and_install_requests():
    try:
        import requests  # noqa: F401
        return
    except ImportError:
        pass

    marker = "/tmp/.ls_requests_checked"
    if exists(marker):
        return
    try:
        with open(marker, "w") as f:
            f.write("1")
    except OSError:
        pass

    python_version = sys.version_info[0]
    if exists("/usr/bin/apt-get"):
        pkg_manager_cmd = "apt-get -y install "
    else:
        pkg_manager_cmd = "opkg install "
    package_name = "python-requests" if python_version == 2 else "python3-requests"
    system(pkg_manager_cmd + package_name)


check_and_install_requests()


# ─── URL decoding ───────────────────────────────────────────────────
PY3 = sys.version_info[0] >= 3
if PY3:
    from urllib.request import urlopen
    from urllib.error import URLError
    from urllib.request import Request
else:
    from urllib2 import urlopen
    from urllib2 import URLError
    from urllib2 import Request


descplug = "Linuxsat-Support.com (Addons Panel)"
PluginLanguageDomain = 'LinuxsatPanel'
PluginLanguagePath = 'Extensions/LinuxsatPanel/locale'
plugin_path = dirname(sys.modules[__name__].__file__)
AgentRequest = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3'
infourl = 'https://raw.githubusercontent.com/OwnerPlugins/upload/main/fill/info.txt'
abouturl = 'https://raw.githubusercontent.com/OwnerPlugins/upload/main/fill/about.txt'
xmlurl = 'https://raw.githubusercontent.com/OwnerPlugins/upload/main/fill/addons_2024.xml'
installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS9MaW51eHNhdFBhbmVsL21haW4vaW5zdGFsbGVyLnNo'
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvTGludXhzYXRQYW5lbA=='

ListUrl = [
    "https://bosscccam.co/Test.php",
    "https://iptv-15days.blogspot.com",
    "https://cccamia.com/free-cccam",
    "https://cccam.net/freecccam"
]


isDreamOS = not exists("/usr/bin/apt-get")


def CheckConn(host='www.google.com', port=80, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as e:
        print('error: ', e)
        return False


def setup_timer(callback_method):
    from enigma import eTimer
    timer = eTimer()
    try:
        timer.timeout.connect(callback_method)
    except BaseException:
        timer.callback.append(callback_method)
    return timer


def version_tuple(version):
    """'2.10.1' -> (2, 10, 1) for a numeric comparison"""
    parts = []
    for part in str(version).strip().split("."):
        try:
            parts.append(int(part))
        except (TypeError, ValueError):
            parts.append(0)
    return tuple(parts) or (0,)


def check_version(currversion, installer_url, AgentRequest):
    """Controllo versione con gestione avanzata formato numerico"""
    print("[Version Check] Starting...")
    remote_version = "0.0"
    remote_changelog = "No changelog available"
    import base64
    try:
        decoded_url = base64.b64decode(installer_url).decode("utf-8")
        if not decoded_url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL protocol")

        req = Request(
            decoded_url,
            headers={
                "User-Agent": AgentRequest,
                "Cache-Control": "no-cache"
            }
        )

        with urlopen(req, timeout=15) as response:
            if response.getcode() != 200:
                raise URLError("HTTP Status: %d" % response.getcode())

            data = response.read().decode("utf-8")

            if data:
                lines = data.split("\n")
                remote_version = "0.0"
                remote_changelog = "No changelog available"

                for line in lines:
                    line = line.strip()
                    if line.startswith("version"):
                        parts = line.split("=")
                        if len(parts) > 1:
                            remote_version = parts[1].strip().strip(
                                "'").strip('"')
                    elif line.startswith("changelog"):
                        parts = line.split("=")
                        if len(parts) > 1:
                            remote_changelog = parts[1].strip().strip(
                                "'").strip('"')
                        break

                new_version = remote_version or "Unknown"
                new_changelog = remote_changelog or "No changelog available"

                return new_version, new_changelog, version_tuple(
                    currversion) < version_tuple(remote_version)

        return None, None, False

    except Exception as e:
        print("Error while checking version:", e)
        return None, None, False


def wgetsts():
    wgetsts = False
    cmd22 = 'find /usr/bin -name "wget"'
    res = popen(cmd22).read()
    if 'wget' not in res.lower():
        if exists("/var/lib/dpkg/status"):
            cmd23 = 'apt-get update && apt-get install wget'
            popen(cmd23)
            wgetsts = True
        else:
            cmd23 = 'opkg update && opkg install wget'
            popen(cmd23)
            wgetsts = True
        return wgetsts


def localeInit():
    if isDreamOS:
        lang = language.getLanguage()[:2]
        environ["LANGUAGE"] = lang
    gettext.bindtextdomain(
        PluginLanguageDomain,
        resolveFilename(
            SCOPE_PLUGINS,
            PluginLanguagePath))


if isDreamOS:
    def _(txt):
        return gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
else:
    def _(txt):
        translated = gettext.dgettext(PluginLanguageDomain, txt)
        if translated:
            return translated
        else:
            print(("[%s] fallback to default translation for %s" %
                  (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
localeInit()
language.addCallback(localeInit)


def getDesktopSize():
    s = getDesktop(0).size()
    return (s.width(), s.height())


def isWQHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] >= 2560


def isFHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] >= 1920


def isHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] <= 1280


def RequestUrl():
    from random import choice
    RandomUrl = choice(ListUrl)
    return RandomUrl


def refreshPlugins():
    from Components.PluginComponent import plugins
    from Tools.Directories import SCOPE_PLUGINS, resolveFilename
    plugins.clearPluginList()
    plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))


try:
    wgetsts()
except BaseException:
    pass


def convert_size(size_bytes):
    import math
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def freespace():
    try:
        stat = statvfs('/')
        free_bytes = stat.f_bfree * stat.f_bsize
        total_bytes = stat.f_blocks * stat.f_bsize
        fspace = convert_size(float(free_bytes))
        total_space = convert_size(float(total_bytes))
        spacestr = _("Free Space:") + " " + str(fspace) + \
            " " + _("of") + " " + str(total_space)
        return spacestr
    except Exception as e:
        print("Error getting disk space:", e)
        return _("Free Space:") + " -?- " + _("of") + " -?-"


def fetch_url(url, retries=3, initial_timeout=5):
    import sys
    import socket
    if sys.version_info[0] == 3:
        from urllib.request import (urlopen)
        from urllib.error import URLError
        PY3 = True
    else:
        from urllib2 import (urlopen)
        from urllib2 import URLError
        PY3 = False
    timeout = initial_timeout
    for i in range(retries):
        try:
            fp = urlopen(url, timeout=timeout)
            lines = fp.readlines()
            fp.close()
            labeltext = ""
            for line in lines:
                if PY3:
                    line = line.decode()
                labeltext += str(line)
            return labeltext
        except socket.timeout:
            print(
                "Attempt failed: The connection timed out after %s seconds." %
                timeout)
            timeout *= 2
        except URLError as e:
            print("URL Error:", e)
            break
        except Exception as e:
            print("Error:", e)
            break
    return None


def checkGZIP(url):
    url = url
    from io import BytesIO
    import gzip
    import sys
    if sys.version_info[0] == 3:
        from urllib.request import (urlopen, Request)
    else:
        from urllib2 import (urlopen, Request)

    hdr = {"User-Agent": AgentRequest}
    response = None
    request = Request(url, headers=hdr)
    try:
        response = urlopen(request, timeout=10)
        if response.info().get('Content-Encoding') == 'gzip':
            buffer = BytesIO(response.read())
            deflatedContent = gzip.GzipFile(fileobj=buffer)
            if sys.version_info[0] == 3:
                return deflatedContent.read().decode('utf-8')
            else:
                return deflatedContent.read()
        else:
            if sys.version_info[0] == 3:
                return response.read().decode('utf-8')
            else:
                return response.read()

    except Exception as e:
        print("Request error:", e)
    return None


def b64decoder(s):
    s = str(s).strip()
    import base64
    import sys
    try:
        output = base64.b64decode(s)
        if sys.version_info[0] == 3:
            output = output.decode('utf-8')
        return output
    except Exception:
        padding = len(s) % 4
        if padding == 1:
            print('Invalid base64 string: {}'.format(s))
            return ""
        elif padding == 2:
            s += '=='
        elif padding == 3:
            s += '='
        else:
            return ""
        output = base64.b64decode(s)
        if sys.version_info[0] == 3:
            output = output.decode('utf-8')
        return output


def make_request(url, max_retries=3, base_delay=1):
    import time
    import socket
    import sys
    import six

    if sys.version_info[0] == 3:
        from urllib.request import (urlopen, Request)
        from urllib.error import URLError
    else:
        from urllib2 import (urlopen, Request)
        from urllib2 import URLError

    for attempt in range(max_retries):
        try:
            req = Request(url)
            req.add_header('User-Agent', AgentRequest)
            response = urlopen(req, None, 30)
            if response.getcode() == 200:
                content = response.read()
                if not content:
                    return None
                try:
                    content = six.ensure_str(content, errors='replace')
                except UnicodeDecodeError:
                    print("Decoding error with 'utf-8', trying 'latin-1'...")
                    content = content.decode('latin-1', errors='replace')
                print("Contenuto decodificato con latin-1:\n", content)
                return content
        except URLError as e:
            if isinstance(e.reason, socket.timeout):
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                print("URLError occurred:", str(e))
                return None
    print("Max retries reached.")
    return None


global lngx
global HALIGN
HALIGN = RT_HALIGN_LEFT
locl = (
    "ar", "ae", "bh", "dz", "eg", "in", "iq", "jo",
    "kw", "lb", "ly", "ma", "om", "qa", "sa", "sd",
    "ss", "sy", "tn", "ye"
)

FNTPath = join(plugin_path, "fonts")
lngx = 'en'


def detect_system_language():
    try:
        from Components.config import config
        lang = config.osd.language.value
        return lang.split('_')[0] if '_' in lang else lang
    except (ImportError, AttributeError, KeyError):
        return lngx


def configure_text_alignment(language_code):
    return RT_HALIGN_RIGHT if language_code in locl else RT_HALIGN_LEFT


def load_custom_fonts(alignment):
    from enigma import addFont
    font_config = {
        RT_HALIGN_RIGHT: {
            'regular': 'DejaVuSans.otf',
            'medium': 'DejaVuSans.otf',
            'bold': 'DejaVuSans.otf'
        },
        RT_HALIGN_LEFT: {
            'regular': 'ls-regular.ttf',
            'medium': 'ls-medium.ttf',
            'bold': 'ls-medium.ttf'
        }
    }
    fonts = font_config[alignment]
    addFont(join(FNTPath, fonts['regular']), 'lsat', 100, 1)
    addFont(join(FNTPath, fonts['medium']), 'lmsat', 100, 1)
    addFont(join(FNTPath, fonts['bold']), 'lbsat', 100, 1)


def initialize_global_settings():
    global HALIGN
    current_language = detect_system_language()
    HALIGN = configure_text_alignment(current_language)
    load_custom_fonts(HALIGN)


def add_skin_fonts():
    from enigma import addFont
    FNTPath = join(plugin_path, "fonts")
    font_config = {
        RT_HALIGN_RIGHT: {
            'regular': 'DejaVuSans.otf',
            'medium': 'DejaVuSans.otf',
            'bold': 'DejaVuSans.otf'
        },
        RT_HALIGN_LEFT: {
            'regular': 'ls-regular.ttf',
            'medium': 'ls-medium.ttf',
            'bold': 'ls-medium.ttf'
        }
    }
    fonts = font_config[HALIGN]
    addFont(join(FNTPath, fonts['regular']), 'lsat', 100, 1)
    addFont(join(FNTPath, fonts['medium']), 'lmsat', 100, 1)
    addFont(join(FNTPath, fonts['bold']), 'lbsat', 100, 1)
