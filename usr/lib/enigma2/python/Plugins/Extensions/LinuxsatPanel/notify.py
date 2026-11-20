#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Linuxsat Panel - commit notifications.

When the panel opens (and periodically while it stays open) it asks GitHub
for the latest commits of the addons repository and counts how many are
newer than the last one the user has seen. That number is the red badge on
the bell. Opening the Commit History marks everything as seen.

Requests are conditional (ETag / If-None-Match): when nothing changed GitHub
answers 304, which does not count against the 60 requests/hour limit.

State lives outside the plugin folder so that updating the plugin does not
reset it.
"""
from __future__ import absolute_import, print_function

import io
import json
import threading
import time
from os import makedirs, rename
from os.path import exists, join

COMMITS_URL = "https://api.github.com/repos/OwnerPlugins/upload/commits"
PER_PAGE = 100

STATE_DIR = "/etc/enigma2/LinuxsatPanel"
STATE_FILE = join(STATE_DIR, "notify.json")
CACHE_FILE = join(STATE_DIR, "commits_cache.json")  # kept with the state:
# a plugin update must not bring back an old cache

USER_AGENT = "LinuxsatPanel"

_lock = threading.Lock()
_state = None


# ─── small file helpers ─────────────────────────────────────────────
def _read_json(path):
    try:
        if exists(path):
            with io.open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print("[Notify] cannot read", path, e)
    return None


def _write_json(path, data):
    try:
        folder = path.rsplit("/", 1)[0]
        if folder and not exists(folder):
            makedirs(folder)
        raw = json.dumps(data, ensure_ascii=False)
        if not isinstance(raw, type(u"")):
            raw = raw.decode("utf-8")
        tmp = path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as f:
            f.write(raw)
        rename(tmp, path)  # atomic: never leave a half-written file
        return True
    except Exception as e:
        print("[Notify] cannot write", path, e)
        return False


def _load():
    global _state
    if _state is None:
        data = _read_json(STATE_FILE)
        if not isinstance(data, dict) or data.get("schema") != 2:
            data = {"schema": 2, "last_seen": None, "etag": None,
                    "unread": 0, "last_check": 0}
        _state = data
    return _state


def _save():
    if _state is not None:
        _write_json(STATE_FILE, _state)


def load_cache():
    data = _read_json(CACHE_FILE)
    return data if isinstance(data, list) else None


# ─── GitHub ─────────────────────────────────────────────────────────
def fetch_commits(force=False):
    """
    Return (commits, status). status is one of:
      "new"        fresh data downloaded
      "unchanged"  GitHub said 304, data comes from the cache
      "ratelimit"  403 from GitHub, data (if any) comes from the cache
      "error"      network problem, data (if any) comes from the cache
    Runs in a worker thread.
    """
    import requests
    with _lock:
        st = _load()
        etag = None if force else st.get("etag")
    cached = load_cache()
    headers = {"User-Agent": USER_AGENT,
               "Accept": "application/vnd.github+json"}
    if etag and cached:
        headers["If-None-Match"] = etag
    try:
        r = requests.get(COMMITS_URL, params={"per_page": PER_PAGE},
                         headers=headers, timeout=20)
    except Exception as e:
        print("[Notify] request failed:", e)
        return cached, "error"

    if r.status_code == 304:
        return cached, "unchanged"
    if r.status_code == 403:
        print("[Notify] GitHub rate limit exceeded")
        return cached, "ratelimit"
    if r.status_code != 200:
        print("[Notify] GitHub HTTP", r.status_code)
        return cached, "error"
    try:
        data = r.json()
    except ValueError:
        return cached, "error"
    if not isinstance(data, list):
        return cached, "error"
    _write_json(CACHE_FILE, data)
    with _lock:
        st = _load()
        st["etag"] = r.headers.get("ETag")
        _save()
    return data, "new"


def _count_new(commits, last_seen):
    for i, c in enumerate(commits):
        if c.get("sha") == last_seen:
            return i
    return len(commits)  # last seen is older than the whole page


def new_shas(commits):
    """SHAs newer than the last seen commit (used to mark them in the list)."""
    with _lock:
        last = _load().get("last_seen")
    if not commits or not last:
        return set()
    n = _count_new(commits, last)
    return set(c.get("sha") for c in commits[:n])


def check():
    """Ask GitHub for news. Returns the unread count (None on failure)."""
    commits, status = fetch_commits()
    if not commits:
        return None
    with _lock:
        st = _load()
        newest = commits[0].get("sha")
        if not st.get("last_seen"):
            # first run ever: nothing is "new", just remember where we are
            st["last_seen"] = newest
            st["unread"] = 0
        else:
            st["unread"] = _count_new(commits, st["last_seen"])
        st["last_check"] = int(time.time())
        _save()
        if st["unread"]:
            print("[Notify] %d new commit(s) [%s]" % (st["unread"], status))
        return st["unread"]


def unread_count():
    with _lock:
        return _load().get("unread", 0) or 0


def get_commit_files(sha):
    """
    Files touched by one commit: list of (status, path), or None on error.
    Commits never change, so the answer is cached on disk forever.
    """
    cache_path = join(STATE_DIR, "commit_files.json")
    with _lock:
        cache = _read_json(cache_path) or {}
    if sha in cache:
        return [tuple(x) for x in cache[sha]]
    import requests
    try:
        r = requests.get(COMMITS_URL + "/" + sha,
                         headers={"User-Agent": USER_AGENT,
                                  "Accept": "application/vnd.github+json"},
                         timeout=20)
    except Exception as e:
        print("[Notify] commit files request failed:", e)
        return None
    if r.status_code != 200:
        print("[Notify] commit files HTTP", r.status_code)
        return None
    try:
        files = [(f.get("status", ""), f.get("filename", ""))
                 for f in r.json().get("files") or []]
    except ValueError:
        return None
    with _lock:
        cache = _read_json(cache_path) or {}
        cache[sha] = files
        if len(cache) > 300:            # keep the file small
            for k in list(cache)[:len(cache) - 300]:
                cache.pop(k, None)
        _write_json(cache_path, cache)
    return files


# ─── small persistent preferences (search history, filters) ─────────
def get_pref(key, default=None):
    with _lock:
        return (_load().get("prefs") or {}).get(key, default)


def set_pref(key, value):
    with _lock:
        st = _load()
        st.setdefault("prefs", {})[key] = value
        _save()


def mark_seen(commits):
    """Called when the Commit History has been shown."""
    if not commits:
        return
    with _lock:
        st = _load()
        st["last_seen"] = commits[0].get("sha")
        st["unread"] = 0
        _save()
