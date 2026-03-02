from __future__ import annotations

import csv
import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

WORD_RE = re.compile(r"[A-Za-z']+")

STOP = {
    "the","and","to","of","a","in","he","his","was","with","that","for","as","on","at","it","had","but","not",
    "is","be","by","or","from","were","this","which","an","they","their","them","i","you","we","she","her","him",
    "me","my","our","us","are","so","if","do","did","been","have","has","having","into","out","up","down","over",
    "what","when","where","why","how","than","then","there","here","very","too","can","could","would","should",
}

LEX_CONFINEMENT = {
    "room","rooms","nursery","bed","beds","door","doors","lock","locked","key","keys","bar","bars","barred",
    "window","windows","wall","walls","wallpaper","gate","gates","fence","fenced","ring","rings","rail","rails",
    "chair","chairs","floor","floors","ceiling","ceilings","paper","pattern","patterns",
}

LEX_SCHEDULE = {
    "day","days","night","nights","morning","mornings","evening","evenings","hour","hours","time","times",
    "rest","rests","resting","sleep","sleeps","sleeping","awake","awoke","wake","waking",
}

LEX_SURVEILLANCE = {
    "watch","watches","watching","see","sees","seeing","seen","look","looks","looking","eye","eyes","observe",
    "observed","observing","notice","noticed","noticing","glance","glanced",
}

LEX_SELF_CENSOR = {
    "write","writes","writing","written","paper","journal","diary","secret","secrets","hide","hides","hiding",
    "conceal","concealed","concealing","quiet","quietly","silence","silent","speak","speaks","speaking",
}

def tokenize(s: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(s)]

def split_windows(tokens: list[str], windows: int) -> list[list[str]]:
    if windows <= 0:
        raise ValueError("windows must be positive")
    n = len(tokens)
    if n == 0:
        return [[] for _ in range(windows)]
    step = n // windows
    rem = n % windows
    out = []
    idx = 0
    for w in range(windows):
        size = step + (1 if w < rem else 0)
        out.append(tokens[idx: idx + size])
        idx += size
    return out

def per_1k(hits: int, words: int) -> float:
    return (hits * 1000.0 / words) if words else 0.0

def count_hits(tokens: Iterable[str], lex: set[str]) -> int:
    return sum(1 for t in tokens if t in lex)

def log_odds(a: int, n_a: int, b: int, n_b: int) -> float:
    # smoothed log-odds (add 0.5) to reduce zero blowups
    return math.log((a + 0.5) / (n_a - a + 0.5)) - math.log((b + 0.5) / (n_b - b + 0.5))

def main() -> None:
    root = Path(__file__).resolve().parents[3]
    text_path = root / "data" / "canonical" / "yellow_wallpaper.txt"
    if not text_path.exists():
        raise SystemExit(
            "Missing canonical text. Run: "
            "python tools/update_canonical.py --tag v0.1.0 --work yellow_wallpaper"
        )

    text = text_path.read_text(encoding="utf-8")
    toks = tokenize(text)
    windows = split_windows(toks, 10)

    out_dir = root / "analysis" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    # window metrics
    wm_path = out_dir / "window_metrics.csv"
    with wm_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "window",
            "start_word",
            "end_word_exclusive",
            "word_count",
            "confinement_hits","confinement_per_1k",
            "schedule_hits","schedule_per_1k",
            "surveillance_hits","surveillance_per_1k",
            "self_censor_hits","self_censor_per_1k",
            "constraint_index_per_1k",
        ])
        start = 0
        for i, win in enumerate(windows, start=1):
            wc = len(win)
            c1 = count_hits(win, LEX_CONFINEMENT)
            c2 = count_hits(win, LEX_SCHEDULE)
            c3 = count_hits(win, LEX_SURVEILLANCE)
            c4 = count_hits(win, LEX_SELF_CENSOR)
            idx = per_1k(c1 + c2 + c3 + c4, wc)
            end = start + wc
            w.writerow([
                i, start, end, wc,
                c1, f"{per_1k(c1,wc):.3f}",
                c2, f"{per_1k(c2,wc):.3f}",
                c3, f"{per_1k(c3,wc):.3f}",
                c4, f"{per_1k(c4,wc):.3f}",
                f"{idx:.3f}",
            ])
            start = end

    # keyness: last vs first window
    first = [t for t in windows[0] if t not in STOP and len(t) >= 3]
    last = [t for t in windows[-1] if t not in STOP and len(t) >= 3]
    cf = Counter(first)
    cl = Counter(last)
    n_f = sum(cf.values())
    n_l = sum(cl.values())

    rows = []
    vocab = set(cf) | set(cl)
    for tok in vocab:
        a = cl.get(tok, 0)
        b = cf.get(tok, 0)
        score = log_odds(a, n_l, b, n_f)
        rows.append((score, tok, b, a))

    rows.sort(key=lambda x: (-x[0], x[1]))
    k_path = out_dir / "keyness_last_vs_first.csv"
    with k_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["token", "first_count", "last_count", "log_odds_last_vs_first"])
        for score, tok, b, a in rows[:80]:
            w.writerow([tok, b, a, f"{score:.6f}"])

    print(f"✅ wrote {wm_path} and {k_path}")

if __name__ == "__main__":
    main()
