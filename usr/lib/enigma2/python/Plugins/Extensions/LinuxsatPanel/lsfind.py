#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Linuxsat Panel - helpers for search and clickable commits.
Pure Python (no Enigma2 imports) so it can be tested on a PC.
"""
from __future__ import absolute_import

import re

_RE_BLOCK = re.compile(r'<plugins cont="(.*?)">(.*?)</plugins>', re.DOTALL)
_RE_PLUGIN = re.compile(
    r'<plugin name="(.*?)".*?<url>"(.*?)"</url>',
    re.DOTALL)

# packages uploaded to OwnerPlugins/upload (old name: Belfagor2005/upload)
RAW_BASE = "https://github.com/OwnerPlugins/upload/raw/main/"


def box_accepts(cat, url, is_dpkg, adult_ok=True):
    """Only what this box can install: ipk on OE2.0, deb on OE2.2+."""
    if cat:
        if is_dpkg and "OE2.0" in cat:
            return False
        if not is_dpkg and "OE2.2" in cat:
            return False
        if not adult_ok and "adult" in cat.lower():
            return False
    if url:
        fn = url.lower().split("?")[0]
        if is_dpkg and fn.endswith(".ipk"):
            return False
        if not is_dpkg and fn.endswith(".deb"):
            return False
    return True


def parse_catalog(data):
    """[(category, name, url), ...] from addons_2024.xml text."""
    out = []
    for cat, block in _RE_BLOCK.findall(data or ""):
        for name, url in _RE_PLUGIN.findall(block):
            out.append((cat.strip(), name.strip(), url.strip()))
    return out


def xml_snippet(entries):
    """Build the text addInstall expects: <plugin name=..><url>"..."</url>."""
    parts = []
    for name, url in entries:
        parts.append('<plugin name="%s"><url>"%s"</url></plugin>' % (
            name.replace('"', "'"), url))
    return "\n".join(parts)


# ─── clickable commits ──────────────────────────────────────────────
def is_automatic(commit):
    """Bot commits and merges ("Hide automatic" filter)."""
    try:
        author = commit["commit"]["author"]["name"] or ""
        msg = commit["commit"]["message"] or ""
    except (KeyError, TypeError):
        return False
    return author.endswith("[bot]") or msg.startswith("Merge branch")


def commit_packages(files, catalog_data, is_dpkg):
    """
    From the files of a commit, the packages this box can install:
    [(name, url), ...]. The name comes from the catalog when the file is
    listed there, otherwise from the file name.
    """
    by_path = {}
    for cat, name, url in parse_catalog(catalog_data):
        if "/raw/main/" in url:
            by_path[url.split("/raw/main/", 1)[1]] = (name, url)
    out = []
    seen = set()
    for status, path in files or []:
        if status == "removed" or not path:
            continue
        low = path.lower()
        if not low.endswith((".ipk", ".deb")):
            continue
        if not box_accepts(None, low, is_dpkg):
            continue
        if path in seen:
            continue
        seen.add(path)
        if path in by_path:
            out.append(by_path[path])
        else:
            out.append((path.rsplit("/", 1)[-1], RAW_BASE + path))
    return out


# ─── unified search ─────────────────────────────────────────────────
def search_all(query, catalog_data, scripts_cfg, is_dpkg, adult_ok=True):
    """
    Search the catalog and scripts.json. Every word of the query must
    appear in the name or category. Returns a list of dicts:
      {"kind": "pkg", "name", "cat", "url"}  or
      {"kind": "script", "name", "cat", "cmd"}
    """
    words = [w for w in (query or "").lower().split() if w]
    if not words:
        return []

    def match(*texts):
        hay = " ".join(t.lower() for t in texts if t)
        return all(w in hay for w in words)

    results = []
    seen = set()
    for cat, name, url in parse_catalog(catalog_data):
        if url in seen or not box_accepts(cat, url, is_dpkg, adult_ok):
            continue
        if match(name, cat, url.rsplit("/", 1)[-1]):
            seen.add(url)
            results.append({"kind": "pkg", "name": name, "cat": cat,
                            "url": url})
    for cat, items in ((scripts_cfg or {}).get("categories") or {}).items():
        for it in items or []:
            cmd = it.get("cmd")
            name = it.get("name")
            if not cmd or not name or cmd in seen:
                continue
            if match(name, cat):
                seen.add(cmd)
                results.append({"kind": "script", "name": name, "cat": cat,
                                "cmd": cmd})

    first = words[0]
    results.sort(key=lambda r: (not r["name"].lower().startswith(first),
                                r["name"].lower()))
    return results


def add_history(history, query, size=10):
    query = (query or "").strip()
    out = [query] + [h for h in (history or []) if h.lower() != query.lower()]
    return [h for h in out if h][:size]
