"""Module `elements` provides access to information on chemical element level."""

from __future__ import annotations

from typing import Final, cast

import re

from collections import defaultdict
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).parent


TableValue = int | float | str | None

ELEMENTS_PARQUET: Final[Path] = HERE / "data/elements.parquet"
ELEMENTS_TABLE_PL: Final[pl.DataFrame] = pl.read_parquet(ELEMENTS_PARQUET)

# noinspection PyTypeChecker
Z_TO_SYMBOL: Final[dict[int, str]] = dict(
    ELEMENTS_TABLE_PL.select("atomic_number", "symbol").iter_rows()
)

# noinspection PyTypeChecker
SYMBOL_TO_Z: Final[dict[str, int]] = dict(
    ELEMENTS_TABLE_PL.select("symbol", "atomic_number").iter_rows()
)

CHEMICAL_FORMULA_ELEMENT_SPEC: Final = re.compile(r"(?P<symbol>[A-Z][a-z]?)(?P<atoms>\d+)?")
"""Regex pattern to recognize one element parts in a chemical formula.

    The pattern recognizes capitalized chemical symbols and an optional atom per molecule numbers.

    Examples:
        >>> CHEMICAL_FORMULA_ELEMENT_SPEC.findall("H2O")
        ["H2", "O"]
"""


def atomic_number(_symbol: str) -> int:
    """Get atomic number (Z) for an element.

    Args:
        _symbol: element by chemical symbol

    Returns:
        int: Z - the atomic number for the element.
    """
    return SYMBOL_TO_Z[_symbol]


z = atomic_number
"""Synonym to atomic_number."""


def symbol(_atomic_number: int) -> str:
    """Get chemical symbol for a given Z (atomic number).

    Args:
        _atomic_number: Z of an element

    Returns:
        str: Chemical symbol
    """
    return Z_TO_SYMBOL[_atomic_number]


def get_property(z_or_symbol: int | str, column: str) -> TableValue:
    """Get column value for an element specified with atomic number or symbol.

    Args:
        z_or_symbol: define either by atomic number or symbol
        column: column name in ELEMENTS_TABLE

    Raises:
        KeyError: if it cannot find the given element.

    Returns:
        The column value for the given element.
    """
    _z = SYMBOL_TO_Z[z_or_symbol] if isinstance(z_or_symbol, str) else z_or_symbol
    try:
        return cast(
            "TableValue",
            ELEMENTS_TABLE_PL.filter(atomic_number=_z).select(column).item(),
        )
    except pl.exceptions.ColumnNotFoundError as ex:
        raise KeyError from ex
    except ValueError as ex:
        raise KeyError from ex


def atomic_mass(z_or_symbol: int | str) -> float:
    """Get standard atomic mass for and Element by atomic number.

    Args:
        z_or_symbol: define either by atomic number or symbol

    Returns:
        Average atomic mass of the Element with the atomic number.
    """
    return cast("float", get_property(z_or_symbol, "molar_mass"))


def name(z_or_symbol: int | str) -> str:
    """Get standard atomic mass for and Element by atomic number.

    Args:
        z_or_symbol: define either by atomic number or symbol

    Returns:
        The name of the element.
    """
    return cast("str", get_property(z_or_symbol, "name"))


def from_molecular_formula(formula: str, *, mass_fraction: bool = False) -> pl.DataFrame:
    """Create dataframe for material from chemical formula.

    Minimalistic parser for chemical formula to define compositions on the fly.

    Symbols of elements are to be in capitalized form: Ge, Si...

    Args:
        formula: ... H20, C2H5OH, etc.
        mass_fraction: define mass fractions instead of atomic (default)

    Examples:
        >>> print(from_molecular_formula("H2O"))
        shape: (2, 2)
        ┌───────────────┬──────────┐
        │ atomic_number ┆ fraction │
        │ ---           ┆ ---      │
        │ u8            ┆ f64      │
        ╞═══════════════╪══════════╡
        │ 1             ┆ 0.666667 │
        │ 8             ┆ 0.333333 │
        └───────────────┴──────────┘
        >>> print(from_molecular_formula("C2H5OH"))
        shape: (3, 2)
        ┌───────────────┬──────────┐
        │ atomic_number ┆ fraction │
        │ ---           ┆ ---      │
        │ u8            ┆ f64      │
        ╞═══════════════╪══════════╡
        │ 1             ┆ 0.666667 │
        │ 6             ┆ 0.222222 │
        │ 8             ┆ 0.111111 │
        └───────────────┴──────────┘
        >>> print(from_molecular_formula("H2O", mass_fraction=True))
        shape: (2, 2)
        ┌───────────────┬──────────┐
        │ atomic_number ┆ fraction │
        │ ---           ┆ ---      │
        │ u8            ┆ f64      │
        ╞═══════════════╪══════════╡
        │ 1             ┆ 0.111907 │
        │ 8             ┆ 0.888093 │
        └───────────────┴──────────┘

    Returns:
        composition
    """
    collector: dict[str, int] = defaultdict(int)
    for m in CHEMICAL_FORMULA_ELEMENT_SPEC.finditer(formula):
        ss = m["symbol"]
        atoms = m["atoms"]
        atoms = 1 if atoms is None else int(atoms)
        collector[ss] += atoms
    symbols = sorted(collector.keys())
    atomic_numbers = [atomic_number(s) for s in symbols]
    if mass_fraction:
        fractions = np.fromiter((collector[s] * atomic_mass(s) for s in symbols), dtype=float)
        total_mass = fractions.sum()
        fractions /= total_mass
    else:
        total_atoms = sum(collector.values())
        fractions = np.fromiter((collector[s] / total_atoms for s in symbols), dtype=float)
    return (
        pl.DataFrame(
            {
                "atomic_number": atomic_numbers,
                "fraction": fractions,
            }
        )
        .cast(dtypes={"atomic_number": pl.UInt8})
        .sort("atomic_number")
    )


__all__ = [
    "ELEMENTS_PARQUET",
    "ELEMENTS_TABLE_PL",
    "SYMBOL_TO_Z",
    "Z_TO_SYMBOL",
    "atomic_mass",
    "atomic_number",
    "from_molecular_formula",
    "get_property",
    "symbol",
    "z",
]


if __name__ == "__main__":
    import xdoctest

    xdoctest.doctest_module(__file__, command="all")
