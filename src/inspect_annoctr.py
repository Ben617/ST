#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]  # .../SM
RAW = PROJECT_ROOT / "data" / "raw" / "annoctr" / "linking_mitre_only"

FILES = {
    "train": RAW / "train.jsonl",
    "val": RAW / "val.jsonl",
    "test": RAW / "test.jsonl",
}


def load_jsonl(path: Path, n: Optional[int] = None) -> List[Dict[str, Any]]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
            if n is not None and len(out) >= n:
                break
    return out


def find_text_field(ex: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Return (field_name, text) for common text keys."""
    for k in ["doc_text", "text", "sentence", "content", "document"]:
        if k in ex and isinstance(ex[k], str):
            return k, ex[k]
    return None, None


def find_tokens_field(ex: Dict[str, Any]) -> Tuple[Optional[str], Optional[List[str]]]:
    """Return (field_name, tokens) for common token keys."""
    for k in ["doc_words", "tokens", "words"]:
        if k in ex and isinstance(ex[k], list) and (len(ex[k]) == 0 or isinstance(ex[k][0], str)):
            return k, ex[k]
    return None, None


def collect_spans_anywhere(ex: Any) -> List[Tuple[int, int, Any]]:
    """
    Tries to find span-like structures in nested dict/list.
    Returns list of (start, end, label_or_obj).
    Accepts:
      - [start, end, label]
      - {"start":..., "end":..., "label":...}
      - {"span":[start,end], "label":...}
    """
    spans: List[Tuple[int, int, Any]] = []

    def rec(obj: Any):
        if isinstance(obj, list):
            # [start, end, label]
            if len(obj) >= 2 and all(isinstance(obj[i], int) for i in [0, 1]):
                start, end = obj[0], obj[1]
                label = obj[2] if len(obj) >= 3 else None
                # sanity: plausible span
                if start >= 0 and end >= 0 and end >= start:
                    spans.append((start, end, label))
            for it in obj:
                rec(it)
        elif isinstance(obj, dict):
            if "start" in obj and "end" in obj and isinstance(obj["start"], int) and isinstance(obj["end"], int):
                spans.append((obj["start"], obj["end"], obj.get("label", obj.get("type"))))
            if "span" in obj and isinstance(obj["span"], list) and len(obj["span"]) >= 2:
                s = obj["span"]
                if isinstance(s[0], int) and isinstance(s[1], int):
                    spans.append((s[0], s[1], obj.get("label", obj.get("type"))))
            for v in obj.values():
                rec(v)

    rec(ex)
    # de-dup
    spans = list(dict.fromkeys(spans))
    return spans


def guess_span_type(
    spans: List[Tuple[int, int, Any]],
    text: Optional[str],
    tokens: Optional[List[str]],
) -> str:
    """
    Heuristic:
      - If we have tokens and many ends <= len(tokens): likely token spans
      - If we have text and many ends <= len(text): likely char spans
    """
    if not spans:
        return "unknown (no spans found)"

    ends = [e for (_, e, _) in spans if isinstance(e, int)]
    token_ok = 0
    char_ok = 0

    if tokens is not None:
        L = len(tokens)
        token_ok = sum(1 for e in ends if 0 <= e <= L)

    if text is not None:
        Lc = len(text)
        char_ok = sum(1 for e in ends if 0 <= e <= Lc)

    if token_ok > char_ok and token_ok >= max(3, int(0.6 * len(ends))):
        return f"token (heuristic: {token_ok}/{len(ends)} ends within #tokens={len(tokens)})"
    if char_ok > token_ok and char_ok >= max(3, int(0.6 * len(ends))):
        return f"char (heuristic: {char_ok}/{len(ends)} ends within #chars={len(text)})"
    # fallback
    return f"ambiguous (token_ok={token_ok}, char_ok={char_ok}, n_spans={len(spans)})"


def main():
    print("== AnnoCTR inspector ==")
    for split, path in FILES.items():
        if not path.exists():
            print(f"[{split}] MISSING: {path}")
            continue

        sample = load_jsonl(path, n=3)
        if not sample:
            print(f"[{split}] empty file: {path}")
            continue

        ex0 = sample[0]
        keys = list(ex0.keys())
        print(f"\n[{split}] file={path}")
        print(f"  keys({len(keys)}): {keys}")

        text_k, text = find_text_field(ex0)
        tok_k, toks = find_tokens_field(ex0)

        if text_k:
            print(f"  text field: {text_k} (chars={len(text)})")
        else:
            print("  text field: NOT FOUND")

        if tok_k:
            print(f"  tokens field: {tok_k} (#tokens={len(toks)})")
            print(f"  tokens preview: {toks[:20]}")
        else:
            print("  tokens field: NOT FOUND")

        spans = collect_spans_anywhere(ex0)
        print(f"  span-like items found: {len(spans)}")
        if spans:
            print(f"  span type guess: {guess_span_type(spans[:100], text, toks)}")
            print("  first 10 spans (start,end,label):")
            for s, e, lab in spans[:10]:
                print(f"    - [{s}, {e}] label={lab}")

            # If we have text and the span looks char-based, show substring for first few
            if text is not None:
                print("  substring preview (first 5, safe slicing):")
                for s, e, lab in spans[:5]:
                    if 0 <= s <= e <= len(text):
                        snippet = text[s:e]
                        snippet = snippet.replace("\n", "\\n")
                        print(f"    - [{s},{e}] '{snippet[:80]}' label={lab}")

        # quick counts across first N lines
        N = 200
        dataN = load_jsonl(path, n=N)
        span_counts = [len(collect_spans_anywhere(ex)) for ex in dataN]
        print(f"  quick stats on first {len(dataN)} lines:")
        print(f"    avg span-like per doc: {sum(span_counts)/len(span_counts):.2f}")
        print(f"    max span-like per doc: {max(span_counts)}")

    print(" inspection finished.")


if __name__ == "__main__":
    main()
