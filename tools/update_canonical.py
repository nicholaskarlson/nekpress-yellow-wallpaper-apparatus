from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

DEFAULT_PRIVATE_REPO = "nicholaskarlson/nekpress-pd-ingest"
ASSETS = ["canonical.txt", "canonical.sha256", "provenance.json"]

def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_sha256_file(p: Path) -> tuple[str, str]:
    line = p.read_text(encoding="utf-8").strip()
    parts = line.split()
    if len(parts) < 2:
        raise ValueError(f"Bad sha256 file format: {p}")
    return parts[0], parts[-1]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="Private ingest release tag, e.g. v0.1.0")
    ap.add_argument("--repo", default=DEFAULT_PRIVATE_REPO, help="Private ingest repo owner/name")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "canonical"
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for asset in ASSETS:
            run(["gh", "release", "download", args.tag, "-R", args.repo, "-p", asset, "--dir", str(td_path)])

        canon = td_path / "canonical.txt"
        sha_file = td_path / "canonical.sha256"
        prov = td_path / "provenance.json"

        expected_sha, expected_name = parse_sha256_file(sha_file)
        if expected_name != "canonical.txt":
            raise RuntimeError(f"canonical.sha256 expected canonical.txt but got: {expected_name}")

        actual_sha = sha256_file(canon)
        if actual_sha != expected_sha:
            raise RuntimeError(f"SHA256 mismatch: expected {expected_sha}, got {actual_sha}")

        shutil.copyfile(canon, out_dir / "love_of_life.txt")
        shutil.copyfile(prov, out_dir / "provenance.json")

        meta = {
            "pinned_from": {"repo": args.repo, "tag": args.tag},
            "canonical_sha256": actual_sha,
        }
        (out_dir / "pin.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"✅ pinned canonical to {out_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
