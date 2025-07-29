from __future__ import annotations
import json, re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Iterable

DATA_PACKAGE = "functionwords.datasets"

@dataclass(frozen=True, slots=True)
class FunctionWordSet:
    name: str
    language: str
    period: str
    categories: dict[str, frozenset[str]]

    @property
    def all(self) -> frozenset[str]:
        return frozenset().union(*self.categories.values())

    def subset(self, keys: Iterable[str]) -> frozenset[str]:
        return frozenset().union(*(self.categories[k] for k in keys))

def _load_json(path: Path) -> FunctionWordSet:
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    cats = {k: frozenset(v) for k, v in raw["categories"].items()}
    return FunctionWordSet(
        name=raw["name"],
        language=raw["language"],
        period=raw["period"],
        categories=cats,
    )

def available_ids() -> list[str]:
    return [p.stem for p in resources.files(DATA_PACKAGE).iterdir() if p.suffix == ".json"]

def load(id_: str = "fr_21c") -> FunctionWordSet:
    if id_ not in available_ids():
        raise ValueError(f"unknown function-word set: {id_}")
    path = resources.files(DATA_PACKAGE) / f"{id_}.json"
    return _load_json(path)        # type: ignore[arg-type]
