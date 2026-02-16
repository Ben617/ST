#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
import site


def find_data_py() -> Path:
    rel_path = Path("relik") / "cli" / "data.py"
    bases = []
    for sp in site.getsitepackages():
        bases.append(Path(sp))
    bases.append(Path(site.getusersitepackages()))
    bases.extend(Path(p) for p in sys.path if isinstance(p, str))

    for b in bases:
        p = b / rel_path
        if p.exists():
            return p
    raise FileNotFoundError("relik/cli/data.py not found")


def main():
    p = find_data_py()
    print(f"✅ Gefunden: {p}")
    txt = p.read_text(encoding="utf-8")

    # already patched?
    if "def _read_last_line_py(" in txt:
        print("✅ tail patch already present.")
        return

    helper = """
def _read_last_line_py(path: str) -> bytes:
    # Windows-safe last-line reader (returns raw bytes like subprocess.check_output)
    import os
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise ValueError("output file missing or empty")
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell()
        # walk backwards until newline
        while pos > 0:
            pos -= 1
            f.seek(pos)
            if f.read(1) == b"\\n":
                break
        return f.readline()
"""

    # Insert helper near top (after imports). We place it after the first occurrence of "logger =" if present,
    # otherwise after the first import block.
    if "logger =" in txt:
        txt = txt.replace("logger = ", helper + "\nlogger = ", 1)
    else:
        # fallback: put at very beginning
        txt = helper + "\n" + txt

    # Replace tail call block:
    # last_line = subprocess.check_output(f"tail -n 1 {output_file}", shell=True)
    txt2 = re.sub(
        r"last_line\s*=\s*subprocess\.check_output\(\s*f[\"']tail\s+-n\s+1\s+\{output_file\}[\"']\s*,\s*shell=True\s*\)",
        "last_line = _read_last_line_py(str(output_file))",
        txt,
    )

    if txt2 == txt:
        # Some versions don't use f-string, patch more loosely
        txt2 = re.sub(
            r"last_line\s*=\s*subprocess\.check_output\(\s*[\"']tail\s+-n\s+1\s+.*output_file.*[\"']\s*,\s*shell=True\s*\)",
            "last_line = _read_last_line_py(str(output_file))",
            txt,
        )

    if txt2 == txt:
        print("⚠️ Konnte tail-Aufruf nicht automatisch ersetzen. Suche in data.py nach 'tail -n 1' und poste die Zeilen.")
        return

    p.write_text(txt2, encoding="utf-8")
    print("✅ tail patch applied.")


if __name__ == "__main__":
    main()
