#!/usr/bin/env python3
"""
add_candidates.py
Windows-safe wrapper to call:
  relik retriever add-candidates <question_encoder> <document_index> <in> <out> --top-k <K> ...

Edit QUESTION_ENCODER and DOCUMENT_INDEX below to match the model/index you want to use.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

# --- CONFIGURE THESE ---
# Quick baseline (replace if you have a MITRE index/encoder)
QUESTION_ENCODER = "sapienzanlp/relik-retriever-e5-base-v2-aida-blink-encoder"
DOCUMENT_INDEX = "sapienzanlp/relik-retriever-e5-base-v2-aida-blink-wikipedia-index"

TOP_K = "100"
BATCH_SIZE = "128"
NUM_WORKERS = "4"
DEVICE = "cpu"  # set "cuda" if you have GPU & proper CUDA + torch
PRECISION = "fp32"  # fp16 requires GPU set-up

# --- paths ---
WIN_DIR = ROOT / "data" / "windowed" / "relik"
OUT_DIR = ROOT / "data" / "candidates" / "relik"
OUT_DIR.mkdir(parents=True, exist_ok=True)

pairs = [
    (WIN_DIR / "train.window.jsonl", OUT_DIR / "train.window.candidates.jsonl"),
    (WIN_DIR / "val.window.jsonl",   OUT_DIR / "val.window.candidates.jsonl"),
    (WIN_DIR / "test.window.jsonl",  OUT_DIR / "test.window.candidates.jsonl"),
]

def find_relik_exe() -> str:
    py = Path(sys.executable).resolve()
    candidates = [
        py.parent / "relik.exe",
        py.parent / "Scripts" / "relik.exe",
        py.parent.parent / "Scripts" / "relik.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    # fallback to PATH name
    return "relik"

def run_cmd(cmd):
    print("RUN:", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)

def main():
    relik_exe = find_relik_exe()
    print("Using relik executable:", relik_exe)

    for inp, out in pairs:
        if not inp.exists():
            print(f"SKIP: input missing: {inp}")
            continue
        print(f"\n==> add-candidates {inp.name} -> {out.name}")
        cmd = [
            relik_exe,
            "retriever",
            "add-candidates",
            QUESTION_ENCODER,
            DOCUMENT_INDEX,
            str(inp),
            str(out),
            "--top-k", TOP_K,
            "--batch-size", BATCH_SIZE,
            "--num-workers", NUM_WORKERS,
            "--device", DEVICE,
            "--precision", PRECISION,
        ]
        run_cmd(cmd)

    print("\n✅ add-candidates finished. Check files in:", OUT_DIR)

if __name__ == "__main__":
    main()
