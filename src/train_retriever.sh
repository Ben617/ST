# Startet Retriever-Training/Fine-Tuning mit relik retriever train

#!/usr/bin/env bash
set -euo pipefail

# Trains/Fine-tunes the retriever.
# Uses a ReLiK config yaml + overrides.
# Pick the config that matches your task (EL vs RE). Example here: NYT-style RE retriever finetune.

CONFIG="relik/retriever/conf/finetune_nyt_iterable_in_batch.yaml"

TRAIN_DPR="data/nyt_like/train-windowed-dpr.jsonl"
VAL_DPR="data/nyt_like/val-windowed-dpr.jsonl"
TEST_DPR="data/nyt_like/test-windowed-dpr.jsonl"

# If you follow ReLiK's pipeline strictly, you typically:
# 1) create-windows
# 2) convert-to-dpr
# and then train retriever on *-dpr.jsonl
#
# If you haven't built DPR files yet, stop here and do that step first.

LANG_MODEL="intfloat/e5-base-v2"

echo "==> training retriever"
relik retriever train "$CONFIG" \
  model.language_model="$LANG_MODEL" \
  data.train_dataset_path="$TRAIN_DPR" \
  data.val_dataset_path="$VAL_DPR" \
  data.test_dataset_path="$TEST_DPR"

echo "done."
