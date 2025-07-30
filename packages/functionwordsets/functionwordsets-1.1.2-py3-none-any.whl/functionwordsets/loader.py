from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import importlib
import pathlib


# ──────────────────────────────────────────────────────────────────
# Dataclass holding one function-word set
# ──────────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class FunctionWordSet:
    name: str
    language: str
    period: str
    categories: dict[str, frozenset[str]]

    @property
    def all(self) -> frozenset[str]:
        """Union of all categories."""
        return frozenset().union(*self.categories.values())

    def subset(self, keys: Iterable[str]) -> frozenset[str]:
        """Union of the selected categories."""
        return frozenset().union(*(self.categories[k] for k in keys))


# ──────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────
_DATASET_DIR = pathlib.Path(__file__).parent / "datasets"


def available_ids() -> list[str]:
    """Return every <stem>.py file found in ./datasets (sorted)."""
    return sorted(
        p.stem
        for p in _DATASET_DIR.glob("*.py")
        if p.name != "__init__.py" and not p.name.startswith("_")
    )


def load(id_: str = "fr_21c") -> FunctionWordSet:
    """Load one dataset and return a frozen FunctionWordSet."""
    if id_ not in available_ids():
        raise ValueError(f"unknown function-word set: {id_}")

    mod = importlib.import_module(f"functionwordsets.datasets.{id_}")
    raw = mod.data  # every dataset exposes a top-level `data` dict

    categories = {k: frozenset(v) for k, v in raw["categories"].items()}

    return FunctionWordSet(
        name=raw["name"],
        language=raw["language"],
        period=raw["period"],
        categories=categories,
    )
