#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data/raw/annoctr/linking_mitre_only"
OUT_DIR = ROOT / "data/index"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "mitre_documents.jsonl"

MITRE_REGEX = re.compile(r"/(T\d+(?:\.\d+)?)")

def extract_mitre_id(link: str | None) -> str | None:
    if not link:
        return None
    match = MITRE_REGEX.search(link)
    return match.group(1) if match else None

def main():
    unique = {}

    for split in ["train", "val", "test"]:
        path = RAW_DIR / f"{split}.jsonl"
        if not path.exists():
            continue

        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ex = json.loads(line)
                except json.JSONDecodeError:
                    continue

                mitre_id = extract_mitre_id(ex.get("label_link"))
                label_title = ex.get("label_title")
                entity_type = ex.get("entity_type")

                if mitre_id and mitre_id not in unique:
                    unique[mitre_id] = {
                        "id": mitre_id,
                        "text": f"{mitre_id} {label_title}",
                        "metadata": {
                            "entity_type": entity_type,
                            "title": label_title
                        }
                    }

    with OUT_FILE.open("w", encoding="utf-8") as f:
        for doc in unique.values():
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"✅ Built {len(unique)} MITRE documents")
    print(f"Saved to: {OUT_FILE}")

if __name__ == "__main__":
    main()
