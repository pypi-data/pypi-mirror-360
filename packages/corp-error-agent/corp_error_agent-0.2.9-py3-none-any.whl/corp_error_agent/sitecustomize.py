"""
corp_error_agent.sitecustomize
Auto‑imported by Python – hooks uncaught exceptions,
posts beacons, and prints a CLI hint when available.
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import threading
import time
import traceback
import uuid
import pydoc
from importlib.metadata import distributions

import requests
from platformdirs import user_cache_dir, user_config_dir

# ── Config knobs ────────────────────────────────────────────────────────────

def _get_backend_url():
    # 1. Check environment variable
    env_url = os.getenv("ERROR_AGENT_URL")
    if env_url:
        return env_url
    # 2. Check config file
    conf_path = pathlib.Path(user_config_dir("corp_error_agent")) / "config.json"
    if conf_path.is_file():
        try:
            with conf_path.open() as f:
                data = json.load(f)
                url = data.get("backend_url")
                if url:
                    return url
        except Exception:
            pass
    # 3. Default
    return "http://127.0.0.1:8000"

BACKEND = _get_backend_url()
ENABLED = os.getenv("ERROR_AGENT_ENABLED", "1") == "1"
HINTS_ENABLED = os.getenv("ERROR_AGENT_HINT", "1") == "1"
CONF_THRESHOLD = 0.60  # min confidence to print hint

SUGGESTION_TIMEOUT = int(os.getenv("ERROR_AGENT_SUGGEST_TIMEOUT", "5"))


ENV_ALLOW = {
    "VIRTUAL_ENV",
    "CONDA_PREFIX",
    "PYTHONPATH",
    "LC_ALL",
    "LANG",
    "TZ",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
}


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_uname_m() -> str:
    """Return the machine architecture (uname -m) in a cross‑platform way."""
    try:
        return platform.uname().machine
    except Exception:
        try:
            return subprocess.check_output(["uname", "-m"], text=True).strip()
        except Exception:
            return "unknown"


def _sha1(b: bytes, n: int = 12) -> str:
    return hashlib.sha1(b).hexdigest()[:n]


def _snapshot_packages():
    lst = [f"{d.metadata['Name'].lower()}=={d.version}" for d in distributions()]
    canon = "|".join(sorted(lst))
    return hashlib.md5(canon.encode()).hexdigest()[:12], lst


def _compute_script_id() -> str:
    try:
        main = pathlib.Path(sys.argv[0]).resolve()
        head = main.read_bytes()[:4096]
        stamp = str(int(main.stat().st_mtime_ns // 1_000_000))
        return _sha1(head + stamp.encode())
    except Exception:  # REPL / unknown script
        return uuid.uuid4().hex[:12]


def _post_async(endpoint: str, payload: dict, timeout: int = 3) -> None:
    """POST the payload in a daemon thread so the interpreter can exit cleanly."""

    def _bg():
        try:
            r = requests.post(f"{BACKEND}{endpoint}", json=payload, timeout=timeout)
            if endpoint == "/beacon" and r.status_code == 204:
                requests.post(f"{BACKEND}/env", json=_ENV_PAYLOAD, timeout=timeout)
        except Exception:
            pass

    threading.Thread(target=_bg, daemon=False).start()  # daemon=True prevents hangs


def _print_hint(h: dict):
    # 1) If the backend sent us a fully formatted blob, page or print that directly
    formatted = h.get("formatted") or h.get("formatted_text")
    if formatted:
        try:
            pydoc.pager(formatted)
        except ImportError:
            sys.stderr.write(formatted + "\n")
        return

    # 2) Otherwise, fall back to the minimal hint
    bar = "─" * 72
    sys.stderr.write(
        f"\n{bar}\n"
        f"💡 corp-error-agent:  {int(h.get('confidence', 0) * 100)} % similar runs:\n"
        f"   {h.get('recommendation', '').strip()}\n"
        f"   More: {h.get('docs', '')}\n"
        f"{bar}\n"
    )


# ── Disable early if env says so ────────────────────────────────────────────
if not ENABLED:
    sys.exit(0)


# ── One‑time snapshots ──────────────────────────────────────────────────────
ARCH = _get_uname_m()
ENV_HASH, PKG_LIST = _snapshot_packages()
SCRIPT_ID = _compute_script_id()
SAFE_ENV = (
    {k: os.environ[k] if k in os.environ else "MISSING" for k in ENV_ALLOW}
    if os.getenv("ERROR_AGENT_ENV", "1") != "0"
    else {}
)

_ENV_PAYLOAD = {
    "env_hash": ENV_HASH,
    "packages": PKG_LIST,
    "python_ver": platform.python_version(),
    "os_info": platform.platform(aliased=True),
    "machine_arch": ARCH, 
    "env_vars": SAFE_ENV,
}

# ── Flag‑file plumbing (error ➜ success) ────────────────────────────────────
CACHE_DIR = pathlib.Path(user_cache_dir("corp_error_agent"))
FLAG_PATH = CACHE_DIR / f"{SCRIPT_ID}.flag"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _flag_exists() -> bool:
    if not FLAG_PATH.is_file():
        return False
    try:
        data = json.loads(FLAG_PATH.read_text())
        if time.time() - data.get("ts", 0) > 7 * 86400:
            FLAG_PATH.unlink(missing_ok=True)
            return False
        return True
    except Exception:
        FLAG_PATH.unlink(missing_ok=True)
        return False


def _write_flag() -> None:
    FLAG_PATH.write_text(json.dumps({"ts": time.time(), "env_hash": ENV_HASH}))


def _delete_flag() -> None:
    FLAG_PATH.unlink(missing_ok=True)


_error_seen = False  # within this Python process only

# ── Uncaught‑exception hook ────────────────────────────────────────────────

def _excepthook(exc_type, exc, tb):
    global _error_seen
    _error_seen = True
    trace = "".join(traceback.format_exception(exc_type, exc, tb))[-25_000:]
    sig = trace.splitlines()[-1].lower().strip() if trace else "unknown"

    _post_async(
        "/beacon",
        {
            "kind": "error",
            "env_hash": ENV_HASH,
            "script_id": SCRIPT_ID,
            "trace": trace,
            "ts": time.time(),
            "error_sig": sig,
        },
    )
    _write_flag()
    
    sys.__excepthook__(exc_type, exc, tb)
    sys.stderr.flush() 

    if HINTS_ENABLED:
        try:
            hint = requests.post(
                f"{BACKEND}/suggest",
                json={"error_sig": sig, "env_hash": ENV_HASH},
                timeout=SUGGESTION_TIMEOUT,
            ).json()
            if hint.get("match") and hint.get("confidence", 0) >= CONF_THRESHOLD:
                _print_hint(hint)
        except Exception:
            pass

    


sys.excepthook = _excepthook

# ── Success beacon at clean exit ───────────────────────────────────────────

def _on_exit() -> None:
    if not _error_seen and _flag_exists():
        _post_async(
            "/beacon",
            {
                "kind": "success",
                "env_hash": ENV_HASH,
                "script_id": SCRIPT_ID,
                "ts": time.time(),
            },
        )
        _delete_flag()


atexit.register(_on_exit)
