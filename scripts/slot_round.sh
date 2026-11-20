#!/bin/bash
# One prompt round on the shared GPU: 45 cards x 3 conditions per arm, all arms in one model load.
#   nohup scripts/slot_round.sh <name> <seed> <kv: auto|fp8> <arm spec> [<arm spec> ...] > data/rounds/<name>.log 2>&1 &
# Arm specs as in storygen/arms.py (name=version[,examples=..|outlines=..|outlines=local]).
# Refuses to start if a compute process that could be a model (> 2 GB) holds the GPU.
set -uo pipefail
NAME=$1; SEED=$2; KV=$3; shift 3
GPU=${GPU_UTIL:-0.78}   # the desktop holds 3.2 to 3.7 GB, so config's 0.86 does not fit (storygen-2)
BT=${BATCHED_TOKENS:-1024}
ARMS=()
for a in "$@"; do ARMS+=(--arm "$a"); done
if nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | awk -F', ' '$2 > 2000' | grep -q .; then
  echo "GPU busy, not starting:"; nvidia-smi --query-compute-apps=pid,used_memory,process_name --format=csv
  exit 3
fi
EXTRA=()
[ "$KV" = fp8 ] && EXTRA=(--kv-cache-dtype fp8)
echo "=== $NAME seed $SEED kv $KV arms: $* $(date)"
CUDA_HOME=/opt/cuda PATH=/opt/cuda/bin:$PATH scripts/capped.sh 10G -- .venv/bin/python -m storygen.generate \
  --out data/rounds/$NAME --cards 45 --seed $SEED --gpu-memory-utilization $GPU --max-num-batched-tokens $BT \
  "${EXTRA[@]}" "${ARMS[@]}"
echo "=== $NAME done rc=$? $(date)"
