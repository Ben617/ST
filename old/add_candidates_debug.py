#!/usr/bin/env python3
"""
add_candidates_debug.py
Führt add-candidates für jeden Split einzeln aus, fängt Fehler ab und schreibt logs:
  logs/add_candidates_train.stdout
  logs/add_candidates_train.stderr
usw.
Passt TOP_K / DEVICE hier an, falls nötig.
"""
from pathlib import Path
import subprocess
import sys
import shlex

ROOT = Path(__file__).resolve().parents[1]
WIN_DIR = ROOT / "data" / "windowed" / "relik"
OUT_DIR = ROOT / "data" / "candidates" / "relik"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Konfiguration ---
QUESTION_ENCODER = "sapienzanlp/relik-retriever-e5-base-v2-aida-blink-encoder"
DOCUMENT_INDEX = "sapienzanlp/relik-retriever-e5-base-v2-aida-blink-wikipedia-index"
TOP_K = "50"        # <-- setze kleiner zum testen (50 statt 100)
BATCH_SIZE = "64"
NUM_WORKERS = "2"
DEVICE = "cpu"
PRECISION = "fp32"

# Splits to run
pairs = [
    ("train", WIN_DIR / "train.window.jsonl", OUT_DIR / "train.window.candidates.jsonl"),
    ("val",   WIN_DIR / "val.window.jsonl",   OUT_DIR / "val.window.candidates.jsonl"),
    ("test",  WIN_DIR / "test.window.jsonl",  OUT_DIR / "test.window.candidates.jsonl"),
]

def find_relik_exe():
    # try common candidate relative to interpreter
    py = Path(sys.executable).resolve()
    candidates = [
        py.parent / "relik.exe",
        py.parent / "Scripts" / "relik.exe",
        py.parent.parent / "Scripts" / "relik.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return "relik"  # fallback to PATH

def run_one(split_name, inp, out):
    relik_exe = find_relik_exe()
    cmd = [
        relik_exe, "retriever", "add-candidates",
        QUESTION_ENCODER, DOCUMENT_INDEX,
        str(inp), str(out),
        "--top-k", TOP_K,
        "--batch-size", BATCH_SIZE,
        "--num-workers", NUM_WORKERS,
        "--device", DEVICE,
        "--precision", PRECISION
    ]
    print(f"\n=== Running for {split_name}:")
    print("CMD:", " ".join(map(str, cmd)))
    stdout_f = LOG_DIR / f"add_candidates_{split_name}.stdout"
    stderr_f = LOG_DIR / f"add_candidates_{split_name}.stderr"

    with stdout_f.open("wb") as out_stdout, stderr_f.open("wb") as out_stderr:
        try:
            proc = subprocess.run(cmd, stdout=out_stdout, stderr=out_stderr, check=True)
            print(f"OK: {split_name} -> wrote {out} (logs in {stdout_f}, {stderr_f})")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: split={split_name} exit={e.returncode}. See logs: {stdout_f} and {stderr_f}")
            # print last 200 chars of stderr for quick glance
            try:
                txt = stderr_f.read_text(encoding="utf-8", errors="ignore")
                print("---- tail of stderr (preview) ----")
                print(txt[-2000:])
            except Exception:
                pass

def main():
    for name, inp, out in pairs:
        if not inp.exists():
            print(f"SKIP {name}: input missing: {inp}")
            continue
        # delete possibly partially created out file first (clean run)
        if out.exists():
            print(f"Removing existing output (clean): {out}")
            out.unlink()
        run_one(name, inp, out)

    print("\nFinished. Check logs/ and data/candidates/relik/")

if __name__ == "__main__":
    main()
