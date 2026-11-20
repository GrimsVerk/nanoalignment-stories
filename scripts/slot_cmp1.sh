#!/bin/bash
# storygen-2 GPU slot: the arm comparison on one card batch (seed 2026112101, 45 cards x 3 conditions),
# then the FP8 KV cache test on the p7 arm. Run from the repo root:
#   nohup scripts/slot_cmp1.sh [bf16|fp8|all] > data/rounds/cmp1.log 2>&1 &
# Refuses to start if another compute process holds the GPU (the bash agent has priority).
set -uo pipefail
WHAT=${1:-all}
SEED=2026112101
OUT=data/rounds/cmp1
EX=data/examples/local.jsonl
mkdir -p data/rounds

gpu_busy() {
  # Compute processes other than tiny desktop helpers (< 200 MiB).
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits |
    awk -F', ' '$2 > 200 {print}' | grep -q .
}

if gpu_busy; then
  echo "GPU busy, not starting:"; nvidia-smi --query-compute-apps=pid,used_memory,process_name --format=csv
  exit 3
fi

ARMS=(--arm p6=p6 --arm p7=p7 --arm "p7_local=p7,examples=$EX"
      --arm "p7_outline=p7,outlines=data/outlines/cmp1.jsonl")
if [ -s data/examples/fable-cmp1.jsonl ]; then
  ARMS+=(--arm "p7_fable=p7,examples=$EX,texts=data/examples/fable-cmp1.jsonl,source=fable")
else
  echo "no Fable examples yet: p7_fable skipped"
fi

if [ "$WHAT" = bf16 ] || [ "$WHAT" = all ]; then
  echo "=== bf16 KV, arms: ${ARMS[*]} $(date)"
  scripts/capped.sh 10G -- .venv/bin/python -m storygen.generate --out $OUT --cards 45 --seed $SEED "${ARMS[@]}"
  echo "=== bf16 done rc=$? $(date)"
fi

if [ "$WHAT" = fp8 ] || [ "$WHAT" = all ]; then
  if gpu_busy; then echo "GPU busy before fp8, stopping"; exit 3; fi
  echo "=== fp8 KV, arm p7 $(date)"
  CUDA_HOME=/opt/cuda PATH=/opt/cuda/bin:$PATH scripts/capped.sh 10G -- .venv/bin/python -m storygen.generate \
    --out $OUT-fp8 --cards 45 --seed $SEED --arm p7=p7 --kv-cache-dtype fp8
  echo "=== fp8 done rc=$? $(date)"
fi
