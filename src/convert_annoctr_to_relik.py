# Haupt-Converter: liest AnnoCTR und schreibt ReLiK-konformes jsonl

#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "annoctr" / "linking_mitre_only"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "relik"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPLITS = {
    "train": RAW_DIR / "train.jsonl",
    "val": RAW_DIR / "val.jsonl",
    "test": RAW_DIR / "test.jsonl",
}

def build_doc_text(ex: Dict[str, Any]) -> str:
    left = ex.get("context_left", "")
    mention = ex.get("mention", "")
    right = ex.get("context_right", "")

    # Robustness: ensure strings
    left = "" if left is None else str(left)
    mention = "" if mention is None else str(mention)
    right = "" if right is None else str(right)

    return left + mention + right

def main():
    for split, in_path in SPLITS.items():
        if not in_path.exists():
            print(f"[{split}] missing input: {in_path}")
            continue

        out_path = OUT_DIR / f"{split}.jsonl"
        n = 0
        dropped = 0

        with in_path.open("r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
            for i, line in enumerate(fin):
                line = line.strip()
                if not line:
                    continue
                ex = json.loads(line)

                mention = ex.get("mention", "")
                context_left = ex.get("context_left", "")
                context_right = ex.get("context_right", "")

                if not mention:
                    dropped += 1
                    continue

                doc_text = build_doc_text(ex)
                start = len(str(context_left))
                end = start + len(str(mention))

                # sanity check
                if end > len(doc_text) or doc_text[start:end] != str(mention):
                    # fallback: try to find mention in doc_text (first occurrence)
                    idx = doc_text.find(str(mention))
                    if idx == -1:
                        dropped += 1
                        continue
                    start = idx
                    end = idx + len(str(mention))

                label_title = ex.get("label_title") or ex.get("label") or "--NME--"

                relik_ex = {
                    "doc_id": i,
                    "doc_text": doc_text,
                    "doc_span_annotations": [
                        [start, end, label_title]
                    ],
                    # keep extra fields for traceability/debugging
                    "meta": {
                        "mention": ex.get("mention"),
                        "label": ex.get("label"),
                        "label_id": ex.get("label_id"),
                        "label_link": ex.get("label_link"),
                        "entity_class": ex.get("entity_class"),
                        "entity_type": ex.get("entity_type"),
                    }
                }

                fout.write(json.dumps(relik_ex, ensure_ascii=False) + "\n")
                n += 1

        print(f"[{split}] wrote {n} examples -> {out_path} (dropped={dropped})")

    print("conversion done.")

if __name__ == "__main__":
    main()
