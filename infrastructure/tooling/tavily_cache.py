#!/usr/bin/env python3
"""
Tavily search with cache‑first logic and timeout fallback.

Uses timeout_wrapper to limit Tavily search execution time (default 30 s).
Caches query results with TTL (default 1 hour for market data, 168 hours for static data).
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any

# Local imports
try:
    from timeout_wrapper import run_with_timeout
except ImportError:
    # fallback for when running as standalone
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from timeout_wrapper import run_with_timeout

TAVILY_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "skills", "tavily-search", "scripts", "search.mjs"
)

CACHE_BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "trading", "execution", "data‑cache", "tavily"
)

def ensure_cache_dir():
    os.makedirs(CACHE_BASE, exist_ok=True)

def cache_path(cache_key: str) -> str:
    return os.path.join(CACHE_BASE, f"{cache_key}.json")

def read_cache(cache_key: str) -> Tuple[Optional[Dict], bool]:
    """
    Read cache file, return (data_dict, is_fresh).
    Freshness determined by 'expires_at' field (ISO timestamp).
    """
    path = cache_path(cache_key)
    if not os.path.exists(path):
        return None, False
    
    try:
        with open(path, "r", encoding="utf‑8") as f:
            data = json.load(f)
    except Exception:
        return None, False
    
    expires = data.get("expires_at")
    if not expires:
        return data, True  # no expiry → treat as fresh
    
    try:
        exp_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        fresh = now < exp_dt
    except Exception:
        fresh = True
    return data, fresh

def write_cache(cache_key: str, answer: str, ttl_hours: int):
    """Write answer to cache with expiry ttl_hours from now."""
    ensure_cache_dir()
    expires = datetime.now(timezone.utc).timestamp() + ttl_hours * 3600
    expires_iso = datetime.fromtimestamp(expires, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    
    data = {
        "query_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expires_at": expires_iso,
        "answer": answer
    }
    
    try:
        with open(cache_path(cache_key), "w", encoding="utf‑8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        # log error
        pass

def extract_answer(raw_output: str) -> str:
    """
    Extract the answer section from Tavily's markdown output.
    Returns empty string if not found.
    """
    # Look for "## Answer" line, take everything until next "##" or end
    lines = raw_output.split('\n')
    in_answer = False
    answer_lines = []
    
    for line in lines:
        if line.startswith("## Answer"):
            in_answer = True
            # Skip the "## Answer" line itself
            continue
        if in_answer and line.startswith("##"):
            # Next section starts
            break
        if in_answer:
            answer_lines.append(line)
    
    answer = '\n'.join(answer_lines).strip()
    return answer

def run_tavily_query(query: str, timeout_seconds: int = 30) -> Tuple[bool, str]:
    """
    Run Tavily search via node script.
    Returns (success, answer_text).
    """
    cmd = f'node "{TAVILY_SCRIPT}" "{query}" --deep -n 5'
    stdout, stderr, exit_code, timed_out = run_with_timeout(cmd, timeout_seconds)
    
    if timed_out:
        return False, f"Tavily query timed out after {timeout_seconds}s"
    
    if exit_code != 0:
        return False, f"Tavily error: {stderr}"
    
    answer = extract_answer(stdout)
    if not answer:
        # No answer section found, maybe the whole output is the answer
        answer = stdout.strip()[:500]  # truncate
    
    return True, answer

def get_tavily_answer(
    query: str,
    cache_key: str,
    ttl_hours: int = 1,
    timeout_seconds: int = 30
) -> Tuple[str, str]:
    """
    Get answer for query using cache‑first with timeout fallback.
    
    Returns (answer_text, status) where status is one of:
    - "fresh_cache": from fresh cache
    - "stale_cache": from stale cache (fetch failed/timed out)
    - "fresh_fetch": newly fetched answer
    - "timeout": fetch timed out, no cache available
    - "error": fetch failed, no cache available
    """
    ensure_cache_dir()
    
    # Try cache first
    cached, fresh = read_cache(cache_key)
    if cached and fresh:
        return cached.get("answer", ""), "fresh_cache"
    
    # Cache stale or missing, try to fetch
    success, answer = run_tavily_query(query, timeout_seconds)
    
    if success:
        write_cache(cache_key, answer, ttl_hours)
        return answer, "fresh_fetch"
    
    # Fetch failed
    if cached:
        # Return stale cache even if expired
        return cached.get("answer", ""), "stale_cache"
    
    # No cache at all
    if "timed out" in answer:
        return "", "timeout"
    return "", "error"

# Predefined queries for morning report
QUERIES = {
    "hsi_price": {
        "query": "HSI Hang Seng Index price today",
        "cache_key": "hsi_price",
        "ttl_hours": 1
    },
    "hscei_price": {
        "query": "Hang Seng China Enterprises Index price today",
        "cache_key": "hscei_price",
        "ttl_hours": 1
    },
    "us_treasury_yields": {
        "query": "US Treasury yields 3M 6M 1Y 2Y today",
        "cache_key": "us_treasury_yields",
        "ttl_hours": 4
    },
    "usd_hkd": {
        "query": "USD/HKD exchange rate today",
        "cache_key": "usd_hkd",
        "ttl_hours": 4
    },
    "hkd_cny": {
        "query": "HKD/CNY exchange rate today",
        "cache_key": "hkd_cny",
        "ttl_hours": 4
    },
    "hk_stock_news": {
        "query": "Hong Kong stock market news today",
        "cache_key": "hk_stock_news",
        "ttl_hours": 4
    },
    "tencent_adr": {
        "query": "Tencent ADR price today",
        "cache_key": "tencent_adr",
        "ttl_hours": 1
    },
    "alibaba_adr": {
        "query": "Alibaba ADR price today",
        "cache_key": "alibaba_adr",
        "ttl_hours": 1
    }
}

def get_report_data() -> Dict[str, Tuple[str, str]]:
    """
    Fetch all data needed for morning report.
    Returns dict: {data_key: (answer_text, status)}
    """
    results = {}
    for key, config in QUERIES.items():
        answer, status = get_tavily_answer(
            config["query"],
            config["cache_key"],
            config["ttl_hours"],
            timeout_seconds=30
        )
        results[key] = (answer, status)
    return results

if __name__ == "__main__":
    # Test with one query
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "HSI Hang Seng Index price today"
    cache_key = "test_query"
    
    answer, status = get_tavily_answer(query, cache_key, ttl_hours=1, timeout_seconds=10)
    print(f"Status: {status}")
    print(f"Answer: {answer[:200]}...")