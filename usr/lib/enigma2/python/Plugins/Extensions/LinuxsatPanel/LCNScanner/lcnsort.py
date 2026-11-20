#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Linuxsat Panel - LCN ordering of the terrestrial (DVB-T) bouquet.

Used after a channel list (settings) is installed: the terrestrial services
saved before the install are put back by Lcn.py, then this module rebuilds
the "Digitale Terrestre" bouquet in LCN order.

No tuning and no screens: the LCN numbers are the ones Enigma2 already
stored during the last terrestrial scan
  1) eDVBDB.getLcnDBData()       (OpenATV 7.x / 8.x, read from memory)
  2) /etc/enigma2/lcndb          (file, format v1 or "#VERSION 2")

Section markers and the range for duplicated numbers come from
LCNScanner/rules.xml (rules name="Default").

Python 2 and 3 compatible, no Enigma2 import at module level, so it can be
tested on a PC.
"""
from __future__ import absolute_import, print_function

import io
import os
import re

E2DIR = "/etc/enigma2"
TV_TYPES = (1, 17, 22, 25, 31, 32, 134, 195)
RADIO_TYPES = (2, 10)
DATA_TYPES = (12, 130, 0x0C, 0x80, 0x81, 0x82)   # OTA, data, not channels
DTT_NS = 0xEEEE

BOUQUET_TV = "userbouquet.terrestrial.tv"
BOUQUET_RADIO = "userbouquet.terrestrial.radio"
BOUQUET_NAME = "Digitale Terrestre"
SPACER = "#SERVICE 1:832:D:0:0:0:0:0:0:0:"
DEFAULT_OVERFLOW = 1000      # first number for duplicated LCNs

LOGFILE = "/tmp/linuxsatpanel_lcn.log"


def log(msg):
    print("[LSP-LCN] %s" % msg)
    try:
        with io.open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(u"%s\n" % msg)
    except Exception:
        pass


def is_dtt(ns):
    return ((ns & 0xFFFFFFFF) >> 16) == DTT_NS


# ---------------------------------------------------------------------------
#  LCN data
# ---------------------------------------------------------------------------
def lcn_from_enigma():
    """[(ns, onid, tsid, sid, lcn, signal)] from Enigma2 memory, or None."""
    try:
        from enigma import eDVBDB
        data = eDVBDB.getInstance().getLcnDBData()
    except Exception:
        return None
    out = []
    for row in data or []:
        try:
            ns, onid, tsid, sid, lcn, signal = row[:6]
            out.append((int(ns), int(onid), int(tsid), int(sid), int(lcn), int(signal)))
        except (TypeError, ValueError):
            continue
    return out or None


def lcn_from_file(path=None):
    """Parse lcndb v1 ("ns:onid:tsid:sid:lcn:signal") or v2 ("#VERSION 2")."""
    path = path or os.path.join(E2DIR, "lcndb")
    out = []
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f]
    version = 2 if lines and lines[0].upper().startswith("#VERSION 2") else 1
    for line in lines:
        if not line or line.startswith("#"):
            continue
        p = line.split(":")
        try:
            if version == 1:
                if len(p) < 6:
                    continue
                ns, onid, tsid, sid = [int(x, 16) for x in p[:4]]
                lcn, signal = int(p[4]), int(p[5])
            else:
                # SID:TSID:ONID:NAMESPACE:SIGNAL:LCN_BROADCAST:LCN_SCANNED:...
                if len(p) < 6:
                    continue
                sid, tsid, onid, ns = [int(x, 16) for x in p[:4]]
                signal, lcn = int(p[4]), int(p[5])
        except ValueError:
            continue
        out.append((ns, onid, tsid, sid, lcn, signal))
    return out


def lcn_from_builder_json(path=None, base=10):
    """
    Fallback for images that do not store LCNs (OpenPLi and others): the LCN
    snapshot saved by the "LCN Setting Builder" plugin, if installed.
    Format: sources -> {src: {type: "T"}, snap: {"onid:tsid:sid": [lcn, name]}}
    """
    path = path or os.path.join(E2DIR, "lcnsettingbuilder.json")
    out = []
    if not os.path.exists(path):
        return out
    try:
        import json
        with io.open(path, encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except Exception as e:
        log("lcnsettingbuilder.json not read: %s" % e)
        return out
    for src in (data.get("sources") or {}).values():
        if not isinstance(src, dict):
            continue
        if ((src.get("src") or {}).get("type") or "T") != "T":
            continue
        for key, val in (src.get("snap") or {}).items():
            try:
                onid, tsid, sid = [int(x, base) for x in key.split(":")[:3]]
                lcn = int(val[0] if isinstance(val, (list, tuple)) else val)
            except (ValueError, TypeError, IndexError):
                continue
            out.append((DTT_NS << 16, onid, tsid, sid, lcn, 0))
    return out


def read_lcns():
    mem = lcn_from_enigma() or []
    fil = lcn_from_file()
    log("LCN rows: enigma2=%d lcndb=%d (%s)" % (
        len(mem), len(fil), "found" if os.path.exists(os.path.join(E2DIR, "lcndb")) else "missing"))
    if mem:
        log("first enigma2 rows: %s" % (mem[:3],))
    seen, data = set(), []
    for d in mem + fil:
        key = (d[0] & 0xFFFFFFFF, d[1], d[2], d[3])
        if key in seen or not is_dtt(d[0]) or d[4] <= 0:
            continue
        seen.add(key)
        data.append(((d[0] & 0xFFFFFFFF),) + tuple(d[1:]))
    log("terrestrial LCN entries: %d" % len(data))
    return data


# ---------------------------------------------------------------------------
#  lamedb (v4 and v5)
# ---------------------------------------------------------------------------
_RE_V5 = re.compile(r'^s:([0-9a-fA-F:]+),"(.*?)"')


def services_from_enigma():
    """Same data as read_services(), from the lists Enigma2 has in memory."""
    try:
        from enigma import eServiceCenter, eServiceReference
    except Exception:
        return {}
    out = {}
    types = TV_TYPES + RADIO_TYPES + (4, 5, 24, 27)
    for kind in (1, 2):
        q = "1:7:%d:0:0:0:0:0:0:0:%s ORDER BY name" % (
            kind, " || ".join("(type == %d)" % t for t in types))
        try:
            lst = eServiceCenter.getInstance().list(eServiceReference(q))
            items = lst and lst.getContent("SN", True) or []
        except Exception as e:
            log("service list error: %s" % e)
            continue
        for ref, name in items:
            p = ref.split(":")
            try:
                stype, sid, tsid, onid, ns = [int(x, 16) for x in p[2:7]]
            except (ValueError, IndexError):
                continue
            if not is_dtt(ns):
                continue
            out.setdefault((onid, tsid, sid), []).append(
                {"ns": ns, "type": stype, "name": name,
                 "ref": "1:0:%X:%X:%X:%X:%X:0:0:0:" % (stype, sid, tsid, onid, ns)})
    return out


def read_services(e2dir=E2DIR):
    """{(onid, tsid, sid): [ {ns, type, name, ref} ]} for terrestrial services."""
    p4 = os.path.join(e2dir, "lamedb")
    p5 = os.path.join(e2dir, "lamedb5")
    out = {}

    def add(sid, ns, tsid, onid, stype, name):
        if not is_dtt(ns):
            return
        ref = "1:0:%X:%X:%X:%X:%X:0:0:0:" % (stype, sid, tsid, onid, ns)
        out.setdefault((onid, tsid, sid), []).append(
            {"ns": ns, "type": stype, "name": name, "ref": ref})

    # Lcn.py restores the terrestrial services into lamedb (v4): prefer it
    if os.path.exists(p4):
        with io.open(p4, encoding="utf-8", errors="ignore") as f:
            lines = [l.rstrip("\r\n") for l in f]
        inside = False
        i = 0
        while i < len(lines):
            line = lines[i]
            if line == "services":
                inside = True
            elif line == "end":
                inside = False
            elif inside:
                p = line.split(":")
                if len(p) >= 6 and i + 1 < len(lines):
                    try:
                        add(int(p[0], 16), int(p[1], 16), int(p[2], 16),
                            int(p[3], 16), int(p[4]), lines[i + 1].strip())
                    except ValueError:
                        pass
                    i += 3
                    continue
            i += 1
    elif os.path.exists(p5):
        with io.open(p5, encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = _RE_V5.match(line)
                if not m:
                    continue
                a = m.group(1).split(":")
                try:
                    add(int(a[0], 16), int(a[1], 16), int(a[2], 16),
                        int(a[3], 16), int(a[4]), m.group(2))
                except (ValueError, IndexError):
                    continue
    return out


# ---------------------------------------------------------------------------
#  rules.xml
# ---------------------------------------------------------------------------
def read_rules(path, name="Default"):
    """(markers {lcn: text} for TV, overflow start)."""
    markers, overflow = {}, DEFAULT_OVERFLOW
    try:
        from xml.etree.ElementTree import parse
        root = parse(path).getroot()
    except Exception as e:
        log("rules.xml not read: %s" % e)
        return markers, overflow
    for rules in root.findall("rules"):
        if rules.get("name") != name:
            continue
        for r in rules.findall("rule"):
            kind = r.get("type")
            text = (r.text or "").strip()
            if kind == "marker" and r.get("mode", "TV") in ("TV", "All", "Both"):
                try:
                    markers[int(r.get("position"))] = text
                except (TypeError, ValueError):
                    pass
            elif kind == "duplicate":
                try:
                    overflow = int((r.get("range") or "").split("-")[0])
                except ValueError:
                    pass
    return markers, overflow


# ---------------------------------------------------------------------------
#  Bouquet
# ---------------------------------------------------------------------------
def assign_numbers(items, overflow):
    """items: [(lcn, signal, ref)] -> ([(number, ref)], moved).
    Same LCN twice: the strongest signal keeps it, the others go to overflow+."""
    items = sorted(items, key=lambda x: (x[0], -x[1]))
    used, moved = {}, []
    for lcn, _sig, ref in items:
        if lcn in used:
            moved.append(ref)
        else:
            used[lcn] = ref
    nxt = max(overflow, 1)
    for ref in moved:
        while nxt in used:
            nxt += 1
        used[nxt] = ref
    return sorted(used.items()), len(moved)


def bouquet_lines(name, entries, markers, spacers=True):
    """Spacers keep channel number == LCN; markers do not take a number."""
    lines = ["#NAME %s" % name]
    # keep only markers whose section (up to the next marker) has channels
    nums = [n for n, _r in entries]
    pos = sorted(markers)
    pending = []
    for i, p in enumerate(pos):
        nxt = pos[i + 1] if i + 1 < len(pos) else None
        if any(n >= p and (nxt is None or n < nxt) for n in nums):
            pending.append((p, markers[p]))
    state = {"m": 0}

    def flush_markers(upto):
        while pending and pending[0][0] <= upto:
            state["m"] += 1
            lines.append("#SERVICE 1:64:%X:0:0:0:0:0:0:0:" % state["m"])
            lines.append("#DESCRIPTION %s" % pending.pop(0)[1])

    expected = 1
    for num, ref in entries:
        if spacers:
            while expected < num:
                flush_markers(expected)
                lines.append(SPACER)
                expected += 1
        flush_markers(num)
        lines.append("#SERVICE %s" % ref)
        expected = num + 1
    return lines


def write_file(path, lines):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        f.write(u"\n".join(lines) + u"\n")
    os.rename(tmp, path)


def register(fname, radio, e2dir=E2DIR):
    """Put the bouquet first in bouquets.tv / bouquets.radio (once)."""
    idx = os.path.join(e2dir, "bouquets.radio" if radio else "bouquets.tv")
    entry = '#SERVICE 1:7:%d:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet' % (
        2 if radio else 1, fname)
    lines = []
    if os.path.exists(idx):
        with io.open(idx, encoding="utf-8", errors="ignore") as f:
            lines = [l.rstrip("\r\n") for l in f if l.strip()]
    if not lines or not lines[0].startswith("#NAME"):
        lines.insert(0, "#NAME User - bouquets (%s)" % ("Radio" if radio else "TV"))
    lines = [l for l in lines if ('"%s"' % fname) not in l]
    lines.insert(1, entry)
    write_file(idx, lines)


def build(rules_path, e2dir=E2DIR, spacers=True, lcns=None):
    """
    Rebuild the terrestrial bouquet(s) in LCN order.
    Returns a dict with counters; tv == 0 means nothing was written (the
    restored bouquet is left as it is).
    """
    stats = {"tv": 0, "radio": 0, "moved": 0, "missing": 0, "reason": ""}
    lcns = read_lcns() if lcns is None else lcns
    services = read_services(e2dir)
    if not services and e2dir == E2DIR:
        services = services_from_enigma()
        log("terrestrial services from Enigma2 memory: %d" % len(services))
    else:
        log("terrestrial services from lamedb: %d" % len(services))
    if not lcns:
        # no LCN stored by Enigma2: try the LCN Setting Builder snapshot,
        # decimal or hex keys, whichever matches more channels
        jpath = os.path.join(e2dir, "lcnsettingbuilder.json")
        best_set, best_hit = [], 0
        for base in (10, 16):
            cand = [d for d in lcn_from_builder_json(jpath, base) if d[4] > 0]
            hit = sum(1 for d in cand if (d[1], d[2], d[3]) in services)
            log("lcnsettingbuilder.json (base %d): %d entries, %d match" % (base, len(cand), hit))
            if hit > best_hit:
                best_set, best_hit = cand, hit
        lcns = best_set
    stats["services"] = len(services)
    stats["lcns"] = len(lcns)
    if not lcns:
        stats["reason"] = "nolcn"
        log("no LCN data: bouquet left unchanged")
        return stats
    if not services:
        stats["reason"] = "noservices"
        log("no terrestrial services: bouquet left unchanged")
        return stats
    markers, overflow = read_rules(rules_path)

    tv, radio = [], []
    best = {}                       # (onid,tsid,sid) -> strongest LCN entry
    for ns, onid, tsid, sid, lcn, signal in lcns:
        key = (onid, tsid, sid)
        if key not in best or signal > best[key][1]:
            best[key] = (ns, signal, lcn)
    for key, (ns, signal, lcn) in best.items():
        cands = services.get(key)
        if not cands:
            stats["missing"] += 1
            continue
        s = next((c for c in cands if c["ns"] == ns), cands[0])
        if s["type"] in RADIO_TYPES:
            radio.append((lcn, signal, s["ref"]))
        elif s["type"] not in DATA_TYPES:
            # TV, including type 0 (some muxes, e.g. Rai 3, do not set it)
            tv.append((lcn, signal, s["ref"]))

    if not tv and not radio:
        stats["reason"] = "nomatch"
        log("LCN entries do not match any service (sample LCN %s / service %s)" % (
            lcns[:2], list(services)[:2]))
        return stats
    if tv:
        entries, moved = assign_numbers(tv, overflow)
        write_file(os.path.join(e2dir, BOUQUET_TV),
                   bouquet_lines(BOUQUET_NAME, entries, markers, spacers))
        register(BOUQUET_TV, False, e2dir)
        stats["tv"] = len(entries)
        stats["moved"] += moved
    if radio:
        entries, moved = assign_numbers(radio, overflow)
        write_file(os.path.join(e2dir, BOUQUET_RADIO),
                   bouquet_lines(BOUQUET_NAME + " Radio", entries, {}, spacers))
        register(BOUQUET_RADIO, True, e2dir)
        stats["radio"] = len(entries)
        stats["moved"] += moved
    log("TV: %(tv)d  radio: %(radio)d  duplicates moved: %(moved)d  "
        "LCN without service: %(missing)d" % stats)
    return stats


def reload_enigma():
    """Reload lists: inside Enigma2 directly, from telnet through OpenWebif."""
    try:
        from enigma import eDVBDB
        db = eDVBDB.getInstance()
        db.reloadServicelist()
        db.reloadBouquets()
        return True
    except Exception:
        pass
    try:
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen
        urlopen("http://127.0.0.1/web/servicelistreload?mode=0", timeout=10).read()
        return True
    except Exception as e:
        log("reload not done (%s): restart Enigma2 to see the bouquet" % e)
        return False


def run_now():
    """Order the terrestrial bouquet now, without installing a channel list."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:  # inside Enigma2: write the in-memory lists first
        from enigma import eDVBDB
        eDVBDB.getInstance().saveServicelist()
    except Exception:
        pass
    stats = build(os.path.join(here, "rules.xml"))
    if stats.get("tv") or stats.get("radio"):
        reload_enigma()
    return stats


if __name__ == "__main__":
    # telnet/ssh:  python /usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/LCNScanner/lcnsort.py
    run_now()
