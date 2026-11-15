#!/usr/bin/env python3
"""Run simple HTTP GET smoke checks from JSON configuration."""
import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

def probe(item, timeout):
    request = urllib.request.Request(item["url"], headers={"User-Agent": "apiprobe/0.1"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except Exception as exc:
        return False, time.perf_counter() - start, str(exc)
    elapsed = time.perf_counter() - start
    expected = int(item.get("expected_status", 200))
    return status == expected, elapsed, f"HTTP {status} (expected {expected})"

def main():
    p = argparse.ArgumentParser(description="Check HTTP endpoints from JSON.")
    p.add_argument("config", type=Path)
    p.add_argument("--timeout", type=float, default=5.0)
    args = p.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    failed = 0
    for item in config.get("checks", []):
        try:
            ok, elapsed, detail = probe(item, args.timeout)
        except (KeyError, ValueError) as exc:
            ok, elapsed, detail = False, 0.0, f"Invalid check: {exc}"
        print(f"{'PASS' if ok else 'FAIL'} {item.get('name', 'unnamed')}: {detail} in {elapsed:.3f}s")
        failed += not ok
    print(f"Summary: {failed} failed")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
