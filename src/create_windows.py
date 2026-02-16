#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPLITS = [
    ("train", ROOT / "data/processed/relik/train.jsonl", ROOT / "data/windowed/relik/train.window.jsonl"),
    ("val",   ROOT / "data/processed/relik/val.jsonl",   ROOT / "data/windowed/relik/val.window.jsonl"),
    ("test",  ROOT / "data/processed/relik/test.jsonl",  ROOT / "data/windowed/relik/test.window.jsonl"),
]


def run_relik_create_windows(inp: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "relik.cli.cli",
        "data", "create-windows",
        str(inp), str(out),
    ]
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    for name, inp, out in SPLITS:
        if not inp.exists():
            print(f"[{name}] missing input: {inp}")
            continue
        print(f"\n==> [{name}] {inp} -> {out}")
        run_relik_create_windows(inp, out)

    print("\n✅ windows created")


if __name__ == "__main__":
    main()
