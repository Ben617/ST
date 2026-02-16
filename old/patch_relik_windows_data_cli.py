#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
import site


def find_data_py() -> Path:
    rel_path = Path("relik") / "cli" / "data.py"
    candidates = []

    for sp in site.getsitepackages():
        candidates.append(Path(sp))
    candidates.append(Path(site.getusersitepackages()))
    candidates.extend(Path(p) for p in sys.path if isinstance(p, str))

    for base in candidates:
        p = base / rel_path
        if p.exists():
            return p
    raise FileNotFoundError(f"Konnte {rel_path} nicht finden.")


def main() -> None:
    p = find_data_py()
    print(f"✅ Gefunden: {p}")

    txt = p.read_text(encoding="utf-8")

    changed = False

    # 1) File reading: ensure UTF-8 (fixes UnicodeDecodeError)
    # Replace: open(input_file)  -> open(input_file, encoding="utf-8")
    # Replace: open(output_file, write_mode) -> open(output_file, write_mode, encoding="utf-8")
    new = re.sub(r"open\((input_file)\)", r"open(\1, encoding='utf-8')", txt)
    if new != txt:
        txt = new
        changed = True

    new = re.sub(r"open\((output_file,\s*write_mode)\)", r"open(\1, encoding='utf-8')", txt)
    if new != txt:
        txt = new
        changed = True

    # 2) Replace wc/awk line counting with pure Python (Windows compatible)
    # We replace the block that calls wc -l ... awk ... by a python count.
    # This is intentionally broad: if we see "wc -l" in the file, we patch that whole call.
    if "wc -l" in txt:
        # Replace any line that builds a wc/awk command with python counting
        txt = re.sub(
            r"total_lines\s*=\s*int\([^\n]*wc\s+-l[^\n]*\)\s*",
            "total_lines = sum(1 for _ in open(input_file, encoding='utf-8'))\n",
            txt,
            flags=re.IGNORECASE,
        )
        # Some versions store it in a variable like `cmd = "wc -l ..."` then run subprocess.
        # If still present, fallback: remove those lines and set total_lines via python.
        if "wc -l" in txt:
            txt = re.sub(
                r".*wc\s+-l.*\n.*awk.*\n.*subprocess.*\n",
                "total_lines = sum(1 for _ in open(input_file, encoding='utf-8'))\n",
                txt,
                flags=re.IGNORECASE,
            )
        changed = True

    if not changed:
        print("ℹ️ Nichts gepatcht (vielleicht schon gefixt oder Code sieht anders aus).")
        print("   Suche manuell in relik/cli/data.py nach 'wc -l' und 'open(input_file)'.")
        return

    p.write_text(txt, encoding="utf-8")
    print("✅ Patch angewendet. Jetzt create-windows erneut starten.")


if __name__ == "__main__":
    main()
