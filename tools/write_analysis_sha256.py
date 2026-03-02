from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


FILES = [
    "window_metrics.csv",
    "keyness_last_vs_first.csv",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="analysis/results", help="Directory containing CSV outputs")
    ap.add_argument("--out", default="analysis/results/analysis.sha256", help="Output sha256 manifest path")
    args = ap.parse_args()

    results_dir = Path(args.results_dir)
    out_path = Path(args.out)

    missing = [name for name in FILES if not (results_dir / name).exists()]
    if missing:
        raise SystemExit(f"Missing analysis outputs: {', '.join(missing)}")

    lines: list[str] = []
    for name in sorted(FILES):
        p = results_dir / name
        lines.append(f"{sha256_file(p)}  {name}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
