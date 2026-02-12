#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- paths ---
RAW_DIR = ROOT / "data" / "raw" / "annoctr" / "linking_mitre_only"
PROC_DIR = ROOT / "data" / "processed" / "relik"
WIN_DIR = ROOT / "data" / "windowed" / "relik"
CAND_DIR = ROOT / "data" / "candidates" / "relik"

# You can switch these on/off
DO_CONVERT = True
DO_CHECK_SPANS = True
DO_STATS = True
DO_WINDOWS = True
DO_CANDIDATES = False   # turn on after relik is installed + you set encoder/index
DO_TRAIN_READER = False # turn on after candidates exist
DO_EVAL = False         # turn on after training / prediction is implemented

# --- retriever/index for candidates (EL baseline) ---
# Fill these once relik is installed and you decided which encoder/index to use
QUESTION_ENCODER = "sapienzanlp/relik-retriever-e5-base-v2-aida-blink-encoder"
DOCUMENT_INDEX = "sapienzanlp/relik-retriever-e5-base-v2-aida-blink-wikipedia-index"
TOP_K = "100"


def run_py(script: str):
    print(f"\n==> python {script}")
    subprocess.run([sys.executable, str(ROOT / "src" / script)], check=True)


def run_relik(args):
    # calls relik as a module, so it works without PATH issues
    cmd = [sys.executable, "-m", "relik"] + args
    print("\n==> " + " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def main():
    # sanity checks
    for name in ["train.jsonl", "val.jsonl", "test.jsonl"]:
        p = RAW_DIR / name
        if not p.exists():
            raise FileNotFoundError(f"Missing raw file: {p}")

    PROC_DIR.mkdir(parents=True, exist_ok=True)
    WIN_DIR.mkdir(parents=True, exist_ok=True)
    CAND_DIR.mkdir(parents=True, exist_ok=True)

    if DO_CONVERT:
        run_py("convert_annoctr_to_relik.py")

    if DO_CHECK_SPANS:
        run_py("check_processed_spans.py")

    if DO_STATS:
        # only if you implemented it; otherwise set DO_STATS=False
        run_py("dataset_stats.py")

    if DO_WINDOWS:
        # EL windows (doc_text), no --is-split-into-words needed
        run_relik(["data", "create-windows",
                   str(PROC_DIR / "train.jsonl"),
                   str(WIN_DIR / "train.window.jsonl")])
        run_relik(["data", "create-windows",
                   str(PROC_DIR / "val.jsonl"),
                   str(WIN_DIR / "val.window.jsonl")])
        run_relik(["data", "create-windows",
                   str(PROC_DIR / "test.jsonl"),
                   str(WIN_DIR / "test.window.jsonl")])

    if DO_CANDIDATES:
        run_relik(["retriever", "add-candidates",
                   QUESTION_ENCODER,
                   DOCUMENT_INDEX,
                   str(WIN_DIR / "train.window.jsonl"),
                   str(CAND_DIR / "train.window.candidates.jsonl"),
                   "--top-k", TOP_K])
        run_relik(["retriever", "add-candidates",
                   QUESTION_ENCODER,
                   DOCUMENT_INDEX,
                   str(WIN_DIR / "val.window.jsonl"),
                   str(CAND_DIR / "val.window.candidates.jsonl"),
                   "--top-k", TOP_K])
        run_relik(["retriever", "add-candidates",
                   QUESTION_ENCODER,
                   DOCUMENT_INDEX,
                   str(WIN_DIR / "test.window.jsonl"),
                   str(CAND_DIR / "test.window.candidates.jsonl"),
                   "--top-k", TOP_K])

    if DO_TRAIN_READER:
        # choose EL reader config (adjust if you use a different one)
        reader_cfg = "relik/reader/conf/large.yaml"
        run_relik(["reader", "train", reader_cfg,
                   f"train_dataset_path={CAND_DIR / 'train.window.candidates.jsonl'}",
                   f"val_dataset_path={CAND_DIR / 'val.window.candidates.jsonl'}",
                   f"test_dataset_path={CAND_DIR / 'test.window.candidates.jsonl'}"])

    if DO_EVAL:
        run_py("eval.py")

    print("run_all finished.")


if __name__ == "__main__":
    main()
