# Ruft relik data create-windows auf.

#!/usr/bin/env bash
set -euo pipefail

# Input: ReLiK-format jsonl (processed)
# Output: windowed jsonl

IN_TRAIN="data/processed/relik/train.jsonl"
IN_VAL="data/processed/relik/val.jsonl"
IN_TEST="data/processed/relik/test.jsonl"

OUT_TRAIN="data/windowed/relik/train.window.jsonl"
OUT_VAL="data/windowed/relik/val.window.jsonl"
OUT_TEST="data/windowed/relik/test.window.jsonl"

mkdir -p "data/windowed/relik"

echo "==> create-windows (train)"
relik data create-windows \
  "$IN_TRAIN" \
  "$OUT_TRAIN" \
  --is-split-into-words \
  --window-size none

echo "==> create-windows (val)"
relik data create-windows \
  "$IN_VAL" \
  "$OUT_VAL" \
  --is-split-into-words \
  --window-size none

# optional: test split may not exist
if [[ -f "$IN_TEST" ]]; then
  echo "==> create-windows (test)"
  relik data create-windows \
    "$IN_TEST" \
    "$OUT_TEST" \
    --is-split-into-words \
    --window-size none
else
  echo "==> skip: no test file at $IN_TEST"
fi

echo " done."
