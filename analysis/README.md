# Quantitative NLP Analysis (Scholar-Facing)

This repo provides reproducible, text-only quantitative analysis of Jack London’s *Love of Life*.

## Starvation Shift Analysis

We operationalize the “lexical collapse” thesis using two lexicons:

- **Civilization/wealth** (e.g., gold, cartridge, cache, gun)
- **Biology/primal** (e.g., wolf, bone, blood, meat, crawl)

We split the story into 10 equal word-count windows and compute:

- civ hits per 1,000 words
- bio hits per 1,000 words
- **shift index = bio_per_1k − civ_per_1k**
- keyness: top rising tokens in last window vs first (log-odds)

## Run

- python tools/build_analysis.py

Outputs:

- analysis/results/window_metrics.csv
- analysis/results/keyness_last_vs_first.csv
- analysis/results/starvation_shift.json
