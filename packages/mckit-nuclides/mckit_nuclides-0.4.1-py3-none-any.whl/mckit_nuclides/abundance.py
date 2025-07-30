"""Methods to change nuclide abundance in compositions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from mckit_nuclides.elements import ELEMENTS_TABLE_PL
from mckit_nuclides.nuclides import NUCLIDES_TABLE_PL

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

MOLAR_MASS_TABLE = (
    ELEMENTS_TABLE_PL.select("atomic_number", "molar_mass")
    .with_columns(pl.lit(0, dtype=pl.UInt16).alias("mass_number"))
    .select("atomic_number", "mass_number", "molar_mass")
    .vstack(NUCLIDES_TABLE_PL.select("atomic_number", "mass_number", "molar_mass"))
    .sort("atomic_number", "mass_number")
)
"""The table contains molar masses for nuclides with specified and not specified mass numbers."""


def convert_to_atomic_fraction(
    composition: pl.DataFrame, fraction_column: str = "fraction"
) -> pl.DataFrame:
    """Change fractions by mass to fractions by atoms.

    Args:
        composition: DataFrame with columns atomic_number, mass_number
        fraction_column: name of column presenting fraction

    Returns:
        DataFrame: df with modified column "fraction"
    """
    composition_columns = composition.columns
    converted = (
        composition.cast(dtypes={"atomic_number": pl.UInt8, "mass_number": pl.UInt16})
        .join(MOLAR_MASS_TABLE, on=["atomic_number", "mass_number"])
        .with_columns((pl.col(fraction_column) / pl.col("molar_mass")).alias(fraction_column))
    )
    return normalize_column(converted, fraction_column).select(composition_columns)


def normalize_column(table: pl.DataFrame, column: str = "fraction") -> pl.DataFrame:
    """Normalize the values in a column to have sum() == 1.0 over the column.

    Args:
        table: ... to normalize
        column: ... over this column

    Returns:
        Result of normalization
    """
    total_fractions = table.select(column).sum().item()
    return table.with_columns(pl.col(column) / total_fractions)


def expand_df_natural_presence(
    composition: pl.DataFrame,
    fraction_column: str = "fraction",
) -> pl.DataFrame:
    """Expand 'natural' presence in composition presented as a DataFrame.

    Args:
        composition: table with columns atomic_number, mass_number (may be 0), fraction
        fraction_column: exact 'fraction' column name

    Returns:
        Expanded composition as a DataFrame.
    """
    composition_columns = composition.columns
    having_mass_numbers = composition.filter(pl.col("mass_number").ne(0))
    not_having_mass_number = composition.filter(pl.col("mass_number").eq(0))
    expanded = (
        not_having_mass_number.join(
            NUCLIDES_TABLE_PL.select("atomic_number", "mass_number", "isotopic_composition").filter(
                pl.col("isotopic_composition").gt(0)
            ),
            on="atomic_number",
        )
        .with_columns(
            (pl.col(fraction_column) * pl.col("isotopic_composition")).alias(fraction_column),
            mass_number=pl.col(
                "mass_number_right"
            ),  # replace 0 with mass_number from nuclides table
        )
        .select(composition_columns)
    )
    return (
        having_mass_numbers.vstack(expanded)
        .group_by("atomic_number", "mass_number")
        .agg(pl.col(fraction_column).sum())
        .sort("atomic_number", "mass_number")
    )


def expand_natural_presence(
    zaf: Iterable[tuple[int, int, float]],
) -> Generator[tuple[int, int, float]]:
    """Convert sequence of nuclide-fraction specification with natural presence.

    Substitute a sequence of nuclides when mass number is specified as 0.
    This means natural presence.

    Args:
        zaf: sequence of atomic number, mass number and fraction

    Yields:
        atomic number, mass_number, and corrected atomic fraction
    """  # DAR401
    for z, a, f in zaf:
        if a != 0:
            yield z, a, f
        else:
            isotopic_compositions = NUCLIDES_TABLE_PL.filter(
                pl.col("atomic_number").eq(z) & pl.col("isotopic_composition").gt(0.0)
            ).select("mass_number", "isotopic_composition")
            for _a, _ic in isotopic_compositions.iter_rows():
                yield z, _a, f * _ic
