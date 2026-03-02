from pathlib import Path

def test_kdp_bullets_exist_and_are_short():
    root = Path(__file__).resolve().parents[1]
    p = root / "content" / "kdp_originality_bullets.txt"
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines, "Expected at least one bullet"
    for ln in lines:
        assert ln.startswith("- "), "Bullets must start with '- '"
        assert len(ln) <= 80, f"Bullet too long ({len(ln)}): {ln}"

def test_package_imports():
    import nekpress_apparatus  # noqa: F401
