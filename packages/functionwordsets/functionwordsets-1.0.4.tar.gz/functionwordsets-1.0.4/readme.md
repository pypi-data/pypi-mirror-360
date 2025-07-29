# functionwords

_Comprehensive multilingual function‑word datasets with a simple Python API_

---

## Overview
`functionworddatasets` is a package that ships ready‑to‑use **stop‑lists** (function‑word lists) for multiple languages and time periods.  Each dataset is stored as a JSON resource and loaded on demand through a small API.

Supported out of the box:
| ID        | Language / period                  | Entries |
|-----------|-------------------------------------|---------|
| `fr_21c`  | French – 21st century               | ≈ 610   |
| `en_21c`  | English – 21st century              | ≈ 540   |
| `es_21c`  | Spanish – 21st century              | ≈ 530   |
| `it_21c`  | Italian – 21st century              | ≈ 520   |
| `nl_21c`  | Dutch – 21st century                | ≈ 460   |
| `oc_13c`  | Occitan – 13th century              | ≈ 320   |
| `la_1cbc` | Classical Latin – 1st c. BCE        | ≈ 320   |

It allows for personalized definition of function words. Function words are sorted by grammatical natures, which can be selected or not, depending on the expected use. 



## 💡 Supported Grammatical Categories

This package provides curated lists of **function words** and **auxiliary forms**. These lists are designed to support linguistic analysis, text preprocessing, token filtering, and computational processing across different corpora.

A user wanting to remove stopwords to build a word cloud or a topic modeling might chose the most extension function words list, while someone working on authorship attribution might adopt a more focused list, depending on the precise context.

The supported grammatical categories include:

### 🗂️ **Determiners**
- **Definite and Indefinite Articles** (`ARTICLES_DETERMINERS`)  
  Mark definiteness or indefiniteness of nouns (e.g., *the*, *un*, *de*, *lo*, *las*).
- **Possessive Determiners** (`POSSESSIVE_DETERMINERS`)  
  Indicate ownership or relationship (e.g., *my*, *ma*, *mi*, *nostre*).

### 🗣️ **Pronouns**
- **Personal Pronouns** (`PERSONAL_PRONOUNS`)  
  Refer to speakers, listeners, or others, including subject, object, and clitic forms (e.g., *I*, *you*, *he*, *me*, *se*).
- **Possessive Pronouns** (`POSSESSIVE_PRONOUNS`)  
  Standalone forms expressing possession (e.g., *mine*, *le mien*, *el mío*).
- **Demonstrative Pronouns** (`DEMONSTRATIVE_PRONOUNS`)  
  Point to specific entities (e.g., *this*, *that*, *aquest*, *ceci*).
- **Indefinite Pronouns** (`INDEFINITE_PRONOUNS`)  
  Refer to nonspecific persons or things (e.g., *someone*, *quelqu'un*, *alguno*).
- **Interrogative Pronouns** (`INTERROGATIVE_PRONOUNS`)  
  Used to ask questions (e.g., *who*, *que*, *qui*, *wat*).

### 🔗 **Linking Words**
- **Prepositions** (`PREPOSITIONS`)  
  Introduce complements indicating place, time, cause, etc. (e.g., *in*, *on*, *de*, *dins*, *sur*).
- **Coordinating Conjunctions** (`COORD_CONJUNCTIONS`)  
  Link words or clauses of equal status (e.g., *and*, *or*, *et*, *o*, *mais*).
- **Subordinating Conjunctions** (`SUBORD_CONJUNCTIONS`)  
  Introduce subordinate clauses (e.g., *that*, *because*, *si*, *perque*).

### 🕊️ **Adverbs and Related Forms**
- **Adverbs** (`ADVERBS`)  
  Modify verbs, adjectives, or other adverbs (e.g., *quickly*, *bien*, *molt*, *totjorn*).
- **Adverbial Locutions** (`ADV_LOCUTIONS`)  
  Multi-word adverbial phrases expressing time, manner, or frequency (e.g., *from time to time*, *de tant en tant*, *de vez en cuando*).

### 🚫 **Negations**
- **Negative Words** (`NEGATIONS`)  
  Express negation or absence (e.g., *not*, *ne*, *pas*, *jamais*, *nunca*).

### ⚙️ **Auxiliaries and Modals**
- **Auxiliary Verbs (e.g., 'to be', 'to have')** (`AUX_ESSER`, `AUX_AVER`)  
  Forms of *to be* and *to have* used for conjugation and periphrasis across languages.
- **Modal Verbs** (`MODAL_VERBS`)  
  Express necessity, possibility, ability, or desire (e.g., *can*, *must*, *poder*, *deber*, *saber*, *voler*).

---

The lists are designed to be **modular** and **language-specific**, allowing easy integration into NLP pipelines for diverse historical and modern languages. New languages and historical variants can be added or customized as needed.


---

## Installation
```bash
pip install functionwords  # from pypi
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
