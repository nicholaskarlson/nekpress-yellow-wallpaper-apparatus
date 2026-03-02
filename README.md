# NEKpress — Love of Life Apparatus (Academic Edition)

Public, MIT-licensed **editorial apparatus** + **text-only analysis** supporting an annotated paperback edition.

**License holder / editor:** Nicholas Elliott Karlson

This repo pins canonical input text from the private ingestion repo as immutable GitHub Release assets:

- `canonical.txt`
- `canonical.sha256`
- `provenance.json`

## Quick start

### 1) Create venv + install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### 2) Pin canonical input (from private repo release tag)

```bash
python tools/update_canonical.py --tag v0.1.0
```

### 3) Run text-only analysis (no graphics)

```bash
python -m nekpress_apparatus.analyze
```

## Key pinned files

- `data/canonical/love_of_life.txt`
- `data/canonical/provenance.json`
- `data/canonical/pin.json`
