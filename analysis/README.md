# Quantitative NLP Analysis (Scholar-Facing)

This repo provides reproducible, text-only quantitative analysis of Charlotte Perkins Gilman’s
*The Yellow Wallpaper*.

The intent is to support a **constraint-first** reading without front-loading spoilers.

## Constraint Window Metrics (draft)

We split the story into 10 equal word-count windows and compute lexicon hits per 1,000 words for:

- **Confinement** (room/door/window/bar/lock language)
- **Schedule** (rest/time/day/night routines)
- **Surveillance** (watch/see/eyes/observe language)
- **Self-censorship** (write/hide/secret/quiet language)

Outputs:

- `analysis/results/window_metrics.csv`
- `analysis/results/keyness_last_vs_first.csv` (top rising tokens, last window vs first, smoothed log-odds)

## Run

```bash
python tools/build_analysis.py
```
