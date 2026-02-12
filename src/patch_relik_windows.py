#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
import site


WIN_SAFE = "csv.field_size_limit(min(sys.maxsize, 2147483647))  # Windows-safe"


def find_document_py() -> Path:
    # Check site-packages locations for relik/retriever/indexers/document.py
    candidates = []

    # 1) Prefer site.getsitepackages (works for normal installs)
    for sp in site.getsitepackages():
        candidates.append(Path(sp))

    # 2) Also check user site
    candidates.append(Path(site.getusersitepackages()))

    # 3) Fallback: sys.path scan
    candidates.extend(Path(p) for p in sys.path if isinstance(p, str))

    rel_path = Path("relik") / "retriever" / "indexers" / "document.py"

    for base in candidates:
        p = base / rel_path
        if p.exists():
            return p

    raise FileNotFoundError(f"Konnte {rel_path} in site-packages / sys.path nicht finden.")


def main() -> None:
    doc_path = find_document_py()
    print(f"✅ Gefunden: {doc_path}")

    txt = doc_path.read_text(encoding="utf-8")

    if WIN_SAFE in txt:
        print("✅ Bereits gepatcht. Nichts zu tun.")
        return

    # Replace the problematic call
    pattern = r"csv\.field_size_limit\(\s*sys\.maxsize\s*\)"
    if not re.search(pattern, txt):
        print("⚠️ Problemzeile nicht gefunden. Suche nach 'field_size_limit' in der Datei und poste die Stelle.")
        return

    patched = re.sub(pattern, WIN_SAFE, txt, count=1)

    # Ensure imports exist (document.py hat meistens csv & sys schon; falls nicht, minimal ergänzen)
    if "import csv" not in patched:
        # insert after the first import line
        patched = re.sub(r"(^import .+$)", r"\1\nimport csv", patched, count=1, flags=re.MULTILINE)

    if "import sys" not in patched:
        patched = re.sub(r"(^import .+$)", r"\1\nimport sys", patched, count=1, flags=re.MULTILINE)

    doc_path.write_text(patched, encoding="utf-8")
    print("✅ Patch angewendet. Starte PyCharm/Run neu und teste: python -m relik --help")


if __name__ == "__main__":
    main()
