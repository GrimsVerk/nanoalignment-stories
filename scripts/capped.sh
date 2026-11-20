#!/bin/bash
# Run a heavy job under a hard memory cap for the whole job (all its processes), no swap.
#   scripts/capped.sh [MEM] -- <cmd...>     e.g. scripts/capped.sh 10G -- uv run python -m storygen.generate ...
# Copied from nanoalignment (bash-c0-1, after an OOM kill). `prlimit --as` is per process; a
# cgroup scope caps the total. Machine limit: heavy jobs < 12 GB.
set -euo pipefail
MEM=10G
if [ "${1:-}" != "--" ]; then MEM=${1:?usage: capped.sh [MEM] -- cmd...}; shift; fi
[ "${1:-}" = "--" ] && shift
exec systemd-run --user --scope --quiet --collect -p MemoryMax="$MEM" -p MemorySwapMax=0 -- "$@"
