from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

def test_package_imports():
    import nekpress_apparatus  # noqa: F401

def test_build_analysis_writes_expected_files():
    root = Path(__file__).resolve().parents[1]

    # Ensure canonical exists (public-domain; OK to keep in repo)
    canon = root / "data" / "canonical" / "yellow_wallpaper.txt"
    canon.parent.mkdir(parents=True, exist_ok=True)
    if not canon.exists():
        canon.write_text("THE YELLOW WALLPAPER\n\nIt is very seldom...\n", encoding="utf-8")

    out_dir = root / "analysis" / "results"
    if out_dir.exists():
        shutil.rmtree(out_dir)

    subprocess.run([sys.executable, "tools/build_analysis.py", "--work", "yellow_wallpaper"], check=True)

    wm = out_dir / "window_metrics.csv"
    kn = out_dir / "keyness_last_vs_first.csv"
    assert wm.exists() and wm.stat().st_size > 0
    assert kn.exists() and kn.stat().st_size > 0

    subprocess.run([sys.executable, "tools/write_analysis_sha256.py"], check=True)
    sha = (out_dir / "analysis.sha256").read_text(encoding="utf-8")
    assert "window_metrics.csv" in sha
    assert "keyness_last_vs_first.csv" in sha
