import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
p = PROJECT_ROOT / "data" /"processed"/"relik"/"train.jsonl"
bad = 0
n = 0

with p.open(encoding="utf-8") as f:
    for line in f:
        ex = json.loads(line)
        s, e, _ = ex["doc_span_annotations"][0]
        mention = ex["meta"]["mention"]
        if ex["doc_text"][s:e] != mention:
            bad += 1
            if bad < 5:
                print("BAD:", ex["doc_text"][s:e], "vs", mention)
        n += 1

print("checked:", n, "bad:", bad)
