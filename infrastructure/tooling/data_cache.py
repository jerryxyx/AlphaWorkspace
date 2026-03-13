#!/usr/bin/env python3
"""
Cache‑first data retrieval for morning report.

Implements:
- Check cache file (JSON) for freshness.
- If fresh, return cached data.
- If stale or missing, call fetch function with timeout.
- If fetch times out or fails, return stale cache (if available) with warning.
- Log cache hits/misses/timeouts to `memory/network‑timeouts.log`.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Tuple
import subprocess

CACHE_BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "trading", "execution", "data‑cache"
)

def log_cache_event(event: str, cache_name: str, details: str = ""):
    """Append cache event to network‑timeouts.log."""
    log_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "memory", "network‑timeouts.log"
    )
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": event,
        "cache": cache_name,
        "details": details
    }
    try:
        with open(log_path, "a", encoding="utf‑8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # silent fail

def read_cache(cache_file: str) -> Tuple[Optional[Dict], bool]:
    """
    Read cache file, return (data_dict, is_fresh).
    Freshness determined by 'expiresAt' field (ISO timestamp).
    """
    path = os.path.join(CACHE_BASE, cache_file)
    if not os.path.exists(path):
        return None, False
    
    try:
        with open(path, "r", encoding="utf‑8") as f:
            data = json.load(f)
    except Exception:
        return None, False
    
    expires = data.get("expiresAt")
    if not expires:
        return data, True  # no expiry → treat as fresh
    
    try:
        exp_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        fresh = now < exp_dt
    except Exception:
        fresh = True
    return data, fresh

def write_cache(cache_file: str, data: Dict, ttl_hours: int = 168):
    """Write data to cache with expiry ttl_hours from now."""
    path = os.path.join(CACHE_BASE, cache_file)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    expires = datetime.now(timezone.utc).timestamp() + ttl_hours * 3600
    expires_iso = datetime.fromtimestamp(expires, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    
    data_to_store = {
        "lastUpdated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expiresAt": expires_iso,
        "data": data.get("data", data)
    }
    
    try:
        with open(path, "w", encoding="utf‑8") as f:
            json.dump(data_to_store, f, indent=2)
    except Exception as e:
        log_cache_event("write_failed", cache_file, str(e))

def get_with_cache(
    cache_file: str,
    fetch_func: Callable[[], Any],
    timeout_seconds: int = 30,
    ttl_hours: int = 168
) -> Tuple[Any, str]:
    """
    Get data via cache‑first with timeout fallback.
    
    Returns (data, status) where status is one of:
    - "fresh_cache": data from fresh cache
    - "stale_cache": data from stale cache (fetch failed/timed out)
    - "fresh_fetch": newly fetched data (cache was stale/missing)
    - "timeout": fetch timed out, no cache available
    - "error": fetch raised exception, no cache available
    """
    # Try cache first
    cached, fresh = read_cache(cache_file)
    if cached and fresh:
        log_cache_event("cache_hit_fresh", cache_file)
        return cached.get("data", cached), "fresh_cache"
    
    # Cache stale or missing, try to fetch
    if cached and not fresh:
        log_cache_event("cache_hit_stale", cache_file, "will attempt refresh")
    
    try:
        # Run fetch with timeout
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
sys.path.insert(0, '{os.path.dirname(__file__)}')
import data_cache as dc
result = dc._call_fetch({repr(fetch_func.__name__)})
print(repr(result))
"""],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        if result.returncode == 0:
            fetched = eval(result.stdout.strip())
            write_cache(cache_file, fetched, ttl_hours)
            log_cache_event("fetch_success", cache_file)
            return fetched, "fresh_fetch"
        else:
            raise RuntimeError(result.stderr)
    except subprocess.TimeoutExpired:
        log_cache_event("fetch_timeout", cache_file, f"timeout {timeout_seconds}s")
        if cached:
            log_cache_event("fallback_stale", cache_file)
            return cached.get("data", cached), "stale_cache"
        return None, "timeout"
    except Exception as e:
        log_cache_event("fetch_error", cache_file, str(e))
        if cached:
            log_cache_event("fallback_stale", cache_file)
            return cached.get("data", cached), "stale_cache"
        return None, "error"

# Helper for subprocess call
def _call_fetch(func_name: str) -> Any:
    # This would need the actual fetch function; placeholder
    return {"error": "fetch not implemented"}

if __name__ == "__main__":
    # Example usage
    def sample_fetch():
        return {"test": "data", "timestamp": datetime.now(timezone.utc).isoformat()}
    
    data, status = get_with_cache("test-cache.json", sample_fetch, timeout_seconds=5)
    print(f"Status: {status}")
    print(f"Data: {json.dumps(data, indent=2)}")