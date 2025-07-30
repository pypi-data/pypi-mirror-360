from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import importlib.util
import pathlib

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

def available_ids() -> list[str]:
    # Trouve les fichiers .py dans le dossier datasets/, sauf __init__.py
    dataset_dir = pathlib.Path(__file__).parent / "datasets"
    return sorted(
        p.stem
        for p in dataset_dir.glob("*.py")
        if p.name != "__init__.py" and not p.name.startswith("_")
    )

def load(id_: str = "fr_21c") -> FunctionWordSet:
    if id_ not in available_ids():
        raise ValueError(f"unknown function-word set: {id_}")
    
    mod = __import__(f"functionwordsets.datasets.{id_}", fromlist=["data"])
    raw = mod.data
    cats = {k: frozenset(v) for k, v in raw["categories"].items()}

    return FunctionWordSet(
        name=raw["name"],
        language=raw["language"],
        period=raw["period"],
        categories=cats,
    )
