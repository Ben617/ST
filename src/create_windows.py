import subprocess
import sys
from pathlib import Path


def find_relik_exe() -> str:
    """
    Find relik executable on Windows reliably.
    - If you're in a venv: <venv>/Scripts/relik.exe
    - If you're using system Python: <python>/Scripts/relik.exe
    """
    py = Path(sys.executable).resolve()

    # venv or system python: try sibling Scripts folder
    candidates = [
        py.parent / "relik.exe",                 # rare but cheap
        py.parent / "Scripts" / "relik.exe",     # system python layout
        py.parent.parent / "Scripts" / "relik.exe",  # venv layout sometimes
    ]

    for c in candidates:
        if c.exists():
            return str(c)

    # Fallback: hope it's on PATH
    return "relik"


ROOT = Path(__file__).resolve().parents[1]

pairs = [
    (ROOT / "data/processed/relik/train.jsonl", ROOT / "data/windowed/relik/train.window.jsonl"),
    (ROOT / "data/processed/relik/val.jsonl",   ROOT / "data/windowed/relik/val.window.jsonl"),
    (ROOT / "data/processed/relik/test.jsonl",  ROOT / "data/windowed/relik/test.window.jsonl"),
]

(ROOT / "data/windowed/relik").mkdir(parents=True, exist_ok=True)

relik_exe = find_relik_exe()
print("Using relik executable:", relik_exe)

for inp, out in pairs:
    subprocess.run([relik_exe, "data", "create-windows", str(inp), str(out)], check=True)

print("✅ windows created")
