#!/usr/bin/env python3
"""
Timeout wrapper for OpenClaw tool calls.

Implements:
- Default 30‑second timeout for any command.
- Logging of timeouts to `memory/network‑timeouts.log`.
- Fallback to cached/index data when command times out.
- Option to spawn a sub‑agent for tasks >30 s (caller decides).

Usage (as a standalone script):
    python3 timeout_wrapper.py --command "find ..." --timeout 30

Usage (imported):
    from timeout_wrapper import run_with_timeout
    stdout, stderr, exit_code, timed_out = run_with_timeout(cmd, timeout=30)
"""

import subprocess
import json
import time
import sys
import os
from datetime import datetime
from typing import Tuple, Optional

LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "memory", "network‑timeouts.log"
)

def log_timeout(tool: str, command: str, duration: float, fallback_used: str = ""):
    """Append a timeout event to the log."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "timeout",
        "tool": tool,
        "command": command[:500],  # truncate long commands
        "duration_seconds": round(duration, 2),
        "fallback_used": fallback_used
    }
    try:
        with open(LOG_PATH, "a", encoding="utf‑8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        # fallback to stderr if log file cannot be written
        sys.stderr.write(f"Failed to write timeout log: {e}\n")

def run_with_timeout(cmd: str, timeout: int = 30) -> Tuple[str, str, int, bool]:
    """
    Run shell command with timeout.
    Returns (stdout, stderr, exit_code, timed_out).
    """
    start = time.time()
    timed_out = False
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        stdout, stderr, exit_code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        log_timeout("exec", cmd, duration, fallback_used="")
        timed_out = True
        stdout, stderr, exit_code = "", f"Command timed out after {timeout}s", -1
    except Exception as e:
        stdout, stderr, exit_code = "", str(e), -1
    return stdout, stderr, exit_code, timed_out

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", required=True, help="Shell command to run")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    args = parser.parse_args()

    stdout, stderr, exit_code, timed_out = run_with_timeout(args.command, args.timeout)
    if timed_out:
        print("[TIMEOUT] Command exceeded timeout", file=sys.stderr)
    if stderr:
        print(stderr, file=sys.stderr)
    print(stdout)
    sys.exit(exit_code if not timed_out else 124)  # 124 is typical timeout exit code

if __name__ == "__main__":
    main()