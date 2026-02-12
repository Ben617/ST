# Startet Reader-Training mit relik reader train.

#!/usr/bin/env bash
set -euo pipefail

# Trains the reader on windowed + candidates jsonl.

# Choose a config. For RE, ReLiK provides:
# relik/reader/conf/large_nyt.yaml, base_nyt.yaml, small_nyt.yaml
CONFIG="relik/reader/conf/large_nyt.yaml"

TRAIN="data/candidates/relik/train.window.candidates.jsonl"
VAL="data/candidates/relik/val.window.candidates.jsonl"
TEST="data/candidates/relik/test.window.candidates.jsonl"

echo "==> training reader"
if [[ -f "$TEST" ]]; then
  relik reader train "$CONFIG" \
    train_dataset_path="$TRAIN" \
    val_dataset_path="$VAL" \
    test_dataset_path="$TEST"
else
  # if no test split, use val as test
  relik reader train "$CONFIG" \
    train_dataset_path="$TRAIN" \
    val_dataset_path="$VAL" \
    test_dataset_path="$VAL"
fi

echo "done."
