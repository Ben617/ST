# relik retriever add-candidates

#!/usr/bin/env bash
set -euo pipefail

# Adds retriever candidates to each window for the Reader training.
# Requires a question encoder + document index (HF repo id or local path).

# >>> Set these two (examples from ReLiK README)
QUESTION_ENCODER="sapienzanlp/relik-retriever-small-nyt-question-encoder"
DOCUMENT_INDEX="sapienzanlp/relik-retriever-small-nyt-document-index"

# If you have your own, replace with your checkpoint/exported encoder and your built index.

IN_TRAIN="data/windowed/relik/train.window.jsonl"
IN_VAL="data/windowed/relik/val.window.jsonl"
IN_TEST="data/windowed/relik/test.window.jsonl"

OUT_TRAIN="data/candidates/relik/train.window.candidates.jsonl"
OUT_VAL="data/candidates/relik/val.window.candidates.jsonl"
OUT_TEST="data/candidates/relik/test.window.candidates.jsonl"

mkdir -p "data/candidates/relik"

TOP_K=100
BATCH_SIZE=128
NUM_WORKERS=4
DEVICE="cuda"     # set "cpu" if needed
INDEX_DEVICE="cpu"
PRECISION="fp16"  # fp32/fp16/bf16

echo "==> add-candidates (train)"
relik retriever add-candidates \
  "$QUESTION_ENCODER" \
  "$DOCUMENT_INDEX" \
  "$IN_TRAIN" \
  "$OUT_TRAIN" \
  --top-k "$TOP_K" \
  --batch-size "$BATCH_SIZE" \
  --num-workers "$NUM_WORKERS" \
  --device "$DEVICE" \
  --index-device "$INDEX_DEVICE" \
  --precision "$PRECISION"

echo "==> add-candidates (val)"
relik retriever add-candidates \
  "$QUESTION_ENCODER" \
  "$DOCUMENT_INDEX" \
  "$IN_VAL" \
  "$OUT_VAL" \
  --top-k "$TOP_K" \
  --batch-size "$BATCH_SIZE" \
  --num-workers "$NUM_WORKERS" \
  --device "$DEVICE" \
  --index-device "$INDEX_DEVICE" \
  --precision "$PRECISION"

if [[ -f "$IN_TEST" ]]; then
  echo "==> add-candidates (test)"
  relik retriever add-candidates \
    "$QUESTION_ENCODER" \
    "$DOCUMENT_INDEX" \
    "$IN_TEST" \
    "$OUT_TEST" \
    --top-k "$TOP_K" \
    --batch-size "$BATCH_SIZE" \
    --num-workers "$NUM_WORKERS" \
    --device "$DEVICE" \
    --index-device "$INDEX_DEVICE" \
    --precision "$PRECISION"
else
  echo "==> skip: no test file at $IN_TEST"
fi

echo " done."
