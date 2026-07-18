#!/bin/bash
# D9: --help guard (exit 0, precedes all positional/root logic; no downstream $VAR to define)
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo "Usage: update.sh [no args]"
  echo "  Hard-reset and pull the ocas-sift skill repo to its latest pushed state."
  echo "  Options:"
  echo "    --help, -h   Show this message and exit."
  exit 0
fi
cd "$(dirname "$0")/.."
git reset --hard HEAD 2>/dev/null
git clean -fd 2>/dev/null
git pull 2>/dev/null
