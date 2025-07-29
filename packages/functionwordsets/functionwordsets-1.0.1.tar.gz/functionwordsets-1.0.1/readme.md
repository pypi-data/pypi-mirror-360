# functionwords

_Comprehensive multilingual function‑word datasets with a simple Python API_

---

## Overview
`functionwords` is a lightweight package that ships ready‑to‑use **stop‑lists** (function‑word lists) for multiple languages and time periods.  Each dataset is stored as a JSON resource and loaded on demand through a small API.

Supported out of the box:
| ID        | Language / period                  | Entries |
|-----------|-------------------------------------|---------|
| `fr_21c`  | French – 21st century               | ≈ 610   |
| `en_21c`  | English – 21st century              | ≈ 540   |
| `es_21c`  | Spanish – 21st century              | ≈ 530   |
| `it_21c`  | Italian – 21st century              | ≈ 520   |
| `nl_21c`  | Dutch – 21st century                | ≈ 460   |
| `la_1cbc` | Classical Latin – 1st c. BCE        | ≈ 320   |

---

## Installation
```bash
pip install functionwords  # once published on PyPI
# or
pip install -e .           # from a cloned repo
```

The library is in Python ≥ 3.8, has zero runtime dependencies, and is <20 kB zipped.

---

## Quick start
```python
import functionwords as fw

# List available datasets
print(fw.available_ids())          # ['fr_21c', 'en_21c', ...]

# Load one set (defaults to fr_21c)
fr = fw.load()                     # equivalent to fw.load('fr_21c')
print(fr.name, len(fr.all))        # "French – 21st century", 610

# Check membership
if 'ne' in fr.all:
    ...

# Build a custom stop‑set: only articles + prepositions
stops = fr.subset(['articles', 'prepositions'])
```

### Command‑line helpers
```bash
# List dataset IDs
fw-list

# Export every French stop‑word to a text file
fw-export fr_21c -o fr.txt

# Export only conjunctions & negations from Spanish as JSON
fw-export es_21c --include coord_conj subord_conj negations -o es_stop.json
```

---

## File format
Every dataset is a single JSON file with this layout:
```json
{
  "name": "English – 21st century",
  "language": "en",
  "period": "21c",
  "categories": {
    "articles": ["the", "a", ...],
    "prepositions": ["in", "on", ...],
    ...
  }
}
```
`functionwords` never changes the file in place, so you are free to edit it in your own fork.

---
