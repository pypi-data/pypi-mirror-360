"""Information on nuclides: masses, natural presence and more."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from pathlib import Path

import polars as pl

from mckit_nuclides.elements import z

if TYPE_CHECKING:
    from mckit_nuclides.elements import TableValue


HERE = Path(__file__).parent

NUCLIDES_PARQUET: Final[Path] = HERE / "data/nuclides.parquet"
NUCLIDES_TABLE_PL: Final = pl.read_parquet(NUCLIDES_PARQUET)


def get_property(z_or_symbol: int | str, mass_number: int, column: str) -> TableValue:
    """Retrieve mass of a nuclide by atomic and mass numbers, a.u.

    Args:
        z_or_symbol: Z or symbol of a nuclide
        mass_number: A
        column: name of column to extract value from

    Raises:
        KeyError: if cannot find the given nuclide.

    Returns:
        Value of a column for the given nuclide.
    """
    _z = z(z_or_symbol) if isinstance(z_or_symbol, str) else z_or_symbol
    try:
        return cast(
            "TableValue",
            NUCLIDES_TABLE_PL.filter(
                pl.col("atomic_number").eq(_z) & pl.col("mass_number").eq(mass_number)
            )
            .select(column)
            .item(),
        )
    except pl.exceptions.ColumnNotFoundError as ex:  # pragma: no cover
        raise KeyError from ex
    except ValueError as ex:  # pragma: no cover
        raise KeyError from ex


def get_nuclide_mass(z_or_symbol: int | str, mass_number: int) -> float:
    """Retrieve mass of a nuclide by atomic and mass numbers, a.u.

    Args:
        z_or_symbol: Z or symbol of a nuclide
        mass_number: A

    Returns:
        Mass of the Nuclide (a.u).
    """
    return cast("float", get_property(z_or_symbol, mass_number, "molar_mass"))
