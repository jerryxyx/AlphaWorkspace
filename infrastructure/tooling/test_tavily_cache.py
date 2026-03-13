#!/usr/bin/env python3
"""
Test tavily_cache module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tavily_cache import get_tavily_answer

def main():
    # Test with a simple query, short timeout
    query = "USD/HKD exchange rate today"
    cache_key = "test_usd_hkd"
    
    print(f"Testing Tavily cache with query: {query}")
    print(f"Cache key: {cache_key}")
    print("-" * 50)
    
    answer, status = get_tavily_answer(
        query, 
        cache_key, 
        ttl_hours=1,
        timeout_seconds=10  # short timeout for test
    )
    
    print(f"Status: {status}")
    print(f"Answer length: {len(answer)} chars")
    if answer:
        print(f"Answer preview: {answer[:200]}...")
    
    # Check cache file
    import json
    cache_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "trading", "execution", "data‑cache", "tavily", f"{cache_key}.json"
    )
    if os.path.exists(cache_path):
        print(f"\nCache file created: {cache_path}")
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
            print(f"Cache expiry: {cache_data.get('expires_at')}")
    else:
        print("\nNo cache file created (fetch may have failed).")
    
    return 0 if answer else 1

if __name__ == "__main__":
    sys.exit(main())