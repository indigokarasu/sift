#!/usr/bin/env python3
"""
Google Custom Search API quota tracker.
Tracks queries per month (QPM) for multiple accounts.
Free tier: 1,000 queries/month per Google account.
State persisted to ~/.hermes/commons/data/ocas-sift/csapi_quota.json.

Accounts:
  owner   -> owner's GOOGLE_PSE_API_KEY
  indigo  -> Indigo's GOOGLE_PSE_API_KEY_INDIGO

Usage:
    python3 csapi_quota.py check [account]          # Check quota (exit 0=yes, 1=no)
    python3 csapi_quota.py increment [account] [n]  # Record N queries (default 1)
    python3 csapi_quota.py reset [account]          # Reset counter
    python3 csapi_quota.py status [account]         # Print quota state as JSON
    python3 csapi_quota.py remaining [account]      # Print queries remaining
    python3 csapi_quota.py all                      # Print all accounts status

    Omit [account] to apply to all accounts.
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta

QUOTA_FILE = os.path.expanduser("~/.hermes/commons/data/ocas-sift/csapi_quota.json")
MONTHLY_LIMIT = 1000
VALID_ACCOUNTS = ["owner", "indigo"]


def load_state():
    """Load quota state from disk. Returns dict keyed by account."""
    if not os.path.exists(QUOTA_FILE):
        return {}
    try:
        with open(QUOTA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(state):
    """Persist quota state to disk."""
    os.makedirs(os.path.dirname(QUOTA_FILE), exist_ok=True)
    with open(QUOTA_FILE, "w") as f:
        json.dump(state, f, indent=2)


def current_month():
    """Return the current month as YYYY-MM."""
    return datetime.now(timezone.utc).strftime("%Y-%m")


def check_and_reset(state, account):
    """Auto-reset counter if we've entered a new month."""
    month = current_month()
    acct = state.get(account, {})
    if acct.get("month") != month:
        if acct.get("month") and acct.get("count", 0) > 0:
            acct.setdefault("history", []).append({
                "month": acct["month"],
                "queries": acct["count"]
            })
            acct["history"] = acct["history"][-12:]
        acct["month"] = month
        acct["count"] = 0
        state[account] = acct
    return state


def next_month():
    """Return the first day of next month as a human-readable date."""
    now = datetime.now(timezone.utc)
    if now.month == 12:
        nxt = now.replace(year=now.year + 1, month=1, day=1)
    else:
        nxt = now.replace(month=now.month + 1, day=1)
    return nxt.strftime("%Y-%m-%d")


def _get_targets(account):
    """Resolve account arg to list of targets."""
    if account and account not in VALID_ACCOUNTS:
        print(f"Unknown account: {account}. Valid: {VALID_ACCOUNTS}")
        sys.exit(2)
    return [account] if account else VALID_ACCOUNTS


def cmd_check(account=None):
    """Check if quota is available. Exit 0 if yes, 1 if exhausted."""
    state = load_state()
    targets = _get_targets(account)
    all_ok = True
    for acct in targets:
        state = check_and_reset(state, acct)
        remaining = MONTHLY_LIMIT - state.get(acct, {}).get("count", 0)
        if remaining <= 0:
            print(f"  {acct}: EXHAUSTED ({state[acct]['count']}/{MONTHLY_LIMIT})")
            all_ok = False
        else:
            print(f"  {acct}: {remaining}/{MONTHLY_LIMIT} remaining")
    save_state(state)
    sys.exit(0 if all_ok else 1)


def cmd_increment(account=None, n=1):
    """Record N queries against the quota for an account."""
    state = load_state()
    targets = _get_targets(account)
    for acct in targets:
        state = check_and_reset(state, acct)
        acct_data = state.get(acct, {"month": current_month(), "count": 0, "history": []})
        acct_data["count"] = acct_data.get("count", 0) + int(n)
        state[acct] = acct_data
        remaining = max(0, MONTHLY_LIMIT - acct_data["count"])
        if remaining == 0:
            print(f"  {acct}: EXHAUSTED ({acct_data['count']}/{MONTHLY_LIMIT}). Resets {next_month()}.")
        else:
            print(f"  {acct}: {acct_data['count']}/{MONTHLY_LIMIT} used, {remaining} remaining.")
    save_state(state)


def cmd_reset(account=None):
    """Manually reset counter for an account (or all)."""
    state = load_state()
    targets = _get_targets(account)
    for acct in targets:
        state = check_and_reset(state, acct)
        state.setdefault(acct, {})["count"] = 0
        print(f"  {acct}: reset to 0/{MONTHLY_LIMIT}")
        save_state(state)


def cmd_status(account=None):
    """Print quota state as JSON."""
    state = load_state()
    targets = _get_targets(account)
    output = {}
    for acct in targets:
        state = check_and_reset(state, acct)
        remaining = max(0, MONTHLY_LIMIT - state.get(acct, {}).get("count", 0))
        output[acct] = {
            "month": state.get(acct, {}).get("month", current_month()),
            "used": state.get(acct, {}).get("count", 0),
            "limit": MONTHLY_LIMIT,
            "remaining": remaining,
            "exhausted": remaining <= 0,
            "resets": next_month(),
            "history": state.get(acct, {}).get("history", [])
        }
    save_state(state)
    if len(targets) == 1:
        print(json.dumps(list(output.values())[0], indent=2))
    else:
        print(json.dumps(output, indent=2))


def cmd_remaining(account=None):
    """Print remaining queries for an account (or all)."""
    state = load_state()
    targets = _get_targets(account)
    for acct in targets:
        state = check_and_reset(state, acct)
        remaining = max(0, MONTHLY_LIMIT - state.get(acct, {}).get("count", 0))
        print(f"  {acct}: {remaining}/{MONTHLY_LIMIT}")
    save_state(state)


COMMANDS = {
    "check": cmd_check,
    "increment": cmd_increment,
    "reset": cmd_reset,
    "status": cmd_status,
    "remaining": cmd_remaining,
}


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__.strip())
        print(f"\nCommands: {', '.join(COMMANDS)}")
        sys.exit(2)

    cmd = sys.argv[1]
    account = None
    n = 1

    # Parse args: check account name vs numeric
    remaining_args = sys.argv[2:]
    for arg in remaining_args:
        if arg in VALID_ACCOUNTS:
            account = arg
        elif arg.isdigit():
            n = int(arg)

    if cmd == "increment":
        cmd_increment(account, n)
    else:
        cmd_increment(account, n) if False else COMMANDS[cmd](account)
