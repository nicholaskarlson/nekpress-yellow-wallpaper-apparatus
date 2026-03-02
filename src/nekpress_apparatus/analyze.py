from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean, median

WORD_RE = re.compile(r"[A-Za-z0-9']+")

def tokenize_words(s: str) -> list[str]:
    return WORD_RE.findall(s)

def split_paragraphs(s: str) -> list[str]:
    paras = [p.strip() for p in s.split("\n\n")]
    return [p for p in paras if p]

def main() -> None:
    root = Path(__file__).resolve().parents[2]
    text_path = root / "data" / "canonical" / "love_of_life.txt"
    if not text_path.exists():
        raise SystemExit("Missing canonical text. Run: python tools/update_canonical.py --tag v0.1.0")

    text = text_path.read_text(encoding="utf-8")
    words = tokenize_words(text)
    paras = split_paragraphs(text)
    para_word_counts = [len(tokenize_words(p)) for p in paras]

    summary = {
        "word_count": len(words),
        "paragraph_count": len(paras),
        "paragraph_word_count": {
            "min": min(para_word_counts) if para_word_counts else 0,
            "max": max(para_word_counts) if para_word_counts else 0,
            "mean": mean(para_word_counts) if para_word_counts else 0,
            "median": median(para_word_counts) if para_word_counts else 0,
        },
    }

    out_dir = root / "outputs" / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Text-Only Analysis (Draft)",
        "",
        f"- Word count: **{summary['word_count']}**",
        f"- Paragraphs: **{summary['paragraph_count']}**",
        "",
        "## Paragraph length (words)",
        f"- min: {summary['paragraph_word_count']['min']}",
        f"- max: {summary['paragraph_word_count']['max']}",
        f"- mean: {summary['paragraph_word_count']['mean']:.2f}",
        f"- median: {summary['paragraph_word_count']['median']:.2f}",
        "",
        "## Genre + context (stub)",
        "TODO: naturalism, Klondike narrative context, publication history.",
        "",
    ]
    (out_dir / "analysis.md").write_text("\n".join(md), encoding="utf-8")
    print(f"✅ wrote {out_dir}/analysis.md and analysis_summary.json")

if __name__ == "__main__":
    main()
