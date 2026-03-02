# NEKpress — The Yellow Wallpaper Apparatus (Critical Edition)

Public, MIT-licensed **editorial apparatus** + **reproducible text-only analysis** supporting the
NEKpress annotated paperback edition of Charlotte Perkins Gilman’s *The Yellow Wallpaper*.

**License holder / editor:** Nicholas Elliott Karlson

This repo pins canonical input text from the private ingestion repo as immutable GitHub Release assets:

- `canonical.txt`
- `canonical.sha256`
- `provenance.json`

Pinned copies live under:

- `data/canonical/yellow_wallpaper.txt`
- `data/canonical/provenance.json`
- `data/canonical/pin.json`

## Quick start

### 1) Pin canonical text from private ingest

Requires `gh` authenticated (and access to the private ingest repo):

```bash
python tools/update_canonical.py --repo nicholaskarlson/nekpress-yellow-wallpaper-ingest --tag v0.1.0 --work yellow_wallpaper
```

### 2) Build analysis outputs (local)

```bash
python tools/build_analysis.py
```

Outputs:

- `analysis/results/window_metrics.csv`
- `analysis/results/keyness_last_vs_first.csv`

### 3) Cut an analysis release (CI)

Push a tag like `v0.1.0-ana1` to trigger the release workflow:

```bash
git tag v0.1.0-ana1
git push origin v0.1.0-ana1
```

## What’s in `content/`

Story-forward apparatus components intended for the paperback build (commentary is used *after* the story text):

- `intro.md` (draft; no spoilers up front)
- `notes.md` (draft; keyed notes for later placement)
- `historical_footnotes.md` (draft)
- `glossary.md` (draft)
- `editorial_principles.md` (determinism, pins, receipts)
- `kdp_originality_bullets.txt` (short bullets for KDP originality disclosures)
