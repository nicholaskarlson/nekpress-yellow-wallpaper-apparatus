from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

WORD_RE = re.compile(r"[A-Za-z']+")

STOP = {
    "the","and","to","of","a","in","he","his","was","with","that","for","as","on","at","it","had","but","not",
    "is","be","by","or","from","were","this","which","an","they","their","them","i","you","we","she","her","him",
}

LEX_CIV = {
    "gold","cartridge","cartridges","cache","gun","rifle","claim","claims","outfit","camp","camps",
    "trail","trails","match","matches","knife","knives","pack","packs","blanket","blankets",
    "tobacco","flour","tea","sugar","coffee","biscuit","biscuits","fire","fires",
    "map","maps","money","dollar","dollars","store","stores","bag","bags",
}

LEX_BIO = {
    "wolf","wolves","bone","bones","blood","meat","crawl","crawled","crawling","starve","starved","starving",
    "hunger","hungry","stomach","teeth","tooth","rib","ribs","flesh",
    "weak","weakened","weakness","pain","ache","ached","aching","cold","freeze","frozen","frost","frostbite",
    "vomit","vomited","vomiting","nausea","thirst","thirsty","wound","wounds",
    "bite","bit","bitten","snarl","snarled","snarling",
}

@dataclass(frozen=True)
class WindowMetrics:
    window: int
    words: int
    civ_hits: int
    bio_hits: int
    civ_per_1k: float
    bio_per_1k: float
    shift: float
    avg_sentence_len: float
    avg_paragraph_len: float

def tokenize(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text)]

def split_sentences(text: str) -> List[str]:
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]

def split_paragraphs(text: str) -> List[str]:
    paras = [p.strip() for p in text.split("\n\n")]
    return [p for p in paras if p]

def per_1k(count: int, n: int) -> float:
    return (count * 1000.0 / n) if n else 0.0

def count_lex(words: List[str], lex: set[str]) -> int:
    return sum(1 for w in words if w in lex)

def log_odds(a: int, na: int, b: int, nb: int, alpha: float = 0.5) -> float:
    return math.log((a + alpha) / (na - a + alpha)) - math.log((b + alpha) / (nb - b + alpha))

def keyness_last_vs_first(first_words: List[str], last_words: List[str], top_n: int = 40) -> List[Tuple[str,int,int,float]]:
    def freq(ws: List[str]) -> Dict[str,int]:
        d: Dict[str,int] = {}
        for w in ws:
            if len(w) < 3 or w in STOP:
                continue
            d[w] = d.get(w, 0) + 1
        return d

    f0 = freq(first_words)
    f9 = freq(last_words)
    vocab = set(f0) | set(f9)

    n0 = sum(f0.values()) or 1
    n9 = sum(f9.values()) or 1

    scored: List[Tuple[str,int,int,float]] = []
    for w in vocab:
        a = f9.get(w, 0)
        b = f0.get(w, 0)
        if a < 2 and b < 2:
            continue
        lo = log_odds(a, n9, b, n0)
        scored.append((w, b, a, lo))

    scored.sort(key=lambda t: t[3], reverse=True)
    return scored[:top_n]

def build(canonical_path: Path, out_dir: Path, windows: int = 10) -> None:
    text = canonical_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    words = tokenize(text)

    n = len(words)
    wsize = math.ceil(n / windows)
    win_words = [words[i*wsize:(i+1)*wsize] for i in range(windows)]

    sents = split_sentences(text)
    sent_lens = [len(tokenize(s)) for s in sents if s.strip()]
    paras = split_paragraphs(text)
    para_lens = [len(tokenize(p)) for p in paras if p.strip()]

    avg_sent = mean(sent_lens) if sent_lens else 0.0
    avg_para = mean(para_lens) if para_lens else 0.0

    metrics: List[WindowMetrics] = []
    for i, ww in enumerate(win_words):
        civ = count_lex(ww, LEX_CIV)
        bio = count_lex(ww, LEX_BIO)
        metrics.append(
            WindowMetrics(
                window=i,
                words=len(ww),
                civ_hits=civ,
                bio_hits=bio,
                civ_per_1k=per_1k(civ, len(ww)),
                bio_per_1k=per_1k(bio, len(ww)),
                shift=per_1k(bio, len(ww)) - per_1k(civ, len(ww)),
                avg_sentence_len=avg_sent,
                avg_paragraph_len=avg_para,
            )
        )

    first = win_words[0] if win_words else []
    last = win_words[-1] if win_words else []
    key = keyness_last_vs_first(first, last, top_n=40)

    out_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "window_metrics.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["window","words","civ_hits","bio_hits","civ_per_1k","bio_per_1k","shift","avg_sentence_len","avg_paragraph_len"])
        for m in metrics:
            w.writerow([m.window,m.words,m.civ_hits,m.bio_hits,f"{m.civ_per_1k:.3f}",f"{m.bio_per_1k:.3f}",f"{m.shift:.3f}",
                        f"{m.avg_sentence_len:.2f}",f"{m.avg_para:.2f}" if False else f"{m.avg_paragraph_len:.2f}"])

    with (out_dir / "keyness_last_vs_first.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["token","first_count","last_count","log_odds_last_minus_first"])
        for token, b, a, lo in key:
            w.writerow([token, b, a, f"{lo:.6f}"])

    summary = {
        "canonical_path": canonical_path.as_posix(),
        "total_words": n,
        "windows": windows,
        "window_size": wsize,
        "lexicons": {"civilization": sorted(LEX_CIV), "biology": sorted(LEX_BIO)},
        "top_keyness": [{"token": t, "first": b, "last": a, "log_odds": lo} for (t,b,a,lo) in key],
    }
    (out_dir / "starvation_shift.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

def main() -> None:
    canonical = Path("data/canonical/love_of_life.txt")
    if not canonical.exists():
        raise SystemExit("Missing canonical. Run: python tools/update_canonical.py --tag v0.1.0")
    build(canonical, Path("analysis/results"), windows=10)
    print("✅ wrote analysis/results/{window_metrics.csv,keyness_last_vs_first.csv,starvation_shift.json}")
