# NEKpress — The Yellow Wallpaper Analysis (Public)

Public, MIT-licensed **quantitative / text-only analysis** supporting a private KDP paperback edition of
Charlotte Perkins Gilman’s *The Yellow Wallpaper*.

This repository intentionally focuses on:

- pinning the **public-domain** canonical story text (from a deterministic private ingest release), and
- generating reproducible **analysis artifacts** (CSV + SHA receipts).

**Editorial apparatus / essays / notes are private** and live only in the paperback build repository.

## License

- Code under `src/` and `tools/` is MIT licensed.
- The pinned Gilman story text is public domain and included here as a pinned input.

## Canonical pin (from private ingest)

Requires `gh` authenticated (and access to the private ingest repo):

```bash
python tools/update_canonical.py --repo nicholaskarlson/nekpress-yellow-wallpaper-ingest --tag v0.1.0 --work yellow_wallpaper
```

Pinned copies live under:

- `data/canonical/yellow_wallpaper.txt`
- `data/canonical/provenance.json`
- `data/canonical/pin.json`

## Build analysis outputs (local)

```bash
python tools/build_analysis.py --work yellow_wallpaper
python tools/write_analysis_sha256.py
```

Outputs (generated, not committed):

- `analysis/results/window_metrics.csv`
- `analysis/results/keyness_last_vs_first.csv`
- `analysis/results/analysis.sha256`

## Cut an analysis release (CI)

Push a tag like `v0.1.0-ana1` to trigger the release workflow:

```bash
git tag v0.1.0-ana1
git push origin v0.1.0-ana1
```
