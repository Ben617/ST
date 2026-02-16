#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# --- HARD LIMITS gegen Freeze/OOM-Spikes (muss vor ML Imports wirken) ---
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

ROOT = Path(__file__).resolve().parents[1]

QUESTION_ENCODER = "sapienzanlp/relik-retriever-e5-base-v2-aida-blink-encoder"
DOCUMENT_INDEX = str(ROOT / "data/index/mitre_index")


# Noch konservativer, weil du SIGKILL gesehen hast:
TOP_K = "10"
BATCH_SIZE = "1"
NUM_WORKERS = "0"

DEVICE = "cpu"
INDEX_DEVICE = "cpu"     # <<< wichtig: explizit setzen
PRECISION = "fp16"

WIN_DIR = ROOT / "data/windowed/relik"
OUT_DIR = ROOT / "data/candidates/relik"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPLITS = [
    ("train", WIN_DIR / "train.window.jsonl", OUT_DIR / "train.window.candidates.jsonl"),
    ("val",   WIN_DIR / "val.window.jsonl",   OUT_DIR / "val.window.candidates.jsonl"),
    ("test",  WIN_DIR / "test.window.jsonl",  OUT_DIR / "test.window.candidates.jsonl"),
]

def run_add_candidates(inp: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "relik.cli.cli",
        "retriever", "add-candidates",
        QUESTION_ENCODER, DOCUMENT_INDEX,
        str(inp), str(out),
        "--top-k", TOP_K,
        "--batch-size", BATCH_SIZE,
        "--num-workers", NUM_WORKERS,
        "--device", DEVICE,
        "--index-device", INDEX_DEVICE,  # <<< neu
        "--precision", PRECISION,
        "--no-log-recall",
    ]
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main() -> None:
    for name, inp, out in SPLITS:
        if not inp.exists():
            print(f"[{name}] missing input: {inp}")
            continue
        print(f"\n==> [{name}] {inp} -> {out}")
        run_add_candidates(inp, out)

    print("\n✅ candidates created")

if __name__ == "__main__":
    main()
