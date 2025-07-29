import os
from collections.abc import Collection, Mapping
from pathlib import Path

import polars as pl


def _filter_genes(df: pl.DataFrame, remove_features: Collection[str]) -> pl.DataFrame:
    if len(remove_features) > 0:
        remove_pattern = "|".join(remove_features)
        df = (
            df.lazy()
            .with_columns(pl.col("gene").cast(pl.String))
            .filter(~pl.col("gene").str.contains(remove_pattern))
            .with_columns(pl.col("gene").cast(pl.Categorical))
            .collect()
        )
    return df


# 10x Xenium
_XENIUM_COLUMNS = {
    "feature_name": "gene",
    "x_location": "x",
    "y_location": "y",
    "z_location": "z",
}

XENIUM_CTRLS = [
    "^BLANK",
    "^DeprecatedCodeword",
    "^Intergenic",
    "^NegControl",
    "^UnassignedCodeword",
]
"""Patterns for Xenium controls"""


def read_Xenium(
    filepath: str | os.PathLike,
    *,
    min_qv: float | None = None,
    remove_features: Collection[str] = XENIUM_CTRLS,
    additional_columns: Collection[str] = [],
    n_threads: int | None = None,
) -> pl.DataFrame:
    """
    Read a Xenium transcripts file.

    Parameters
    ----------
    filepath : os.PathLike or str
        Path to the Xenium transcripts file. Both, .csv.gz and .parquet files, are supported.
    min_qv : float | None, optional
        Minimum Phred-scaled quality value (Q-Score) of a transcript to be included.
        If `None` no filtering is performed.
    remove_features : collections.abc.Collection[str], optional
        List of regex patterns to filter the 'feature_name' column,
        :py:attr:`ovrlpy.io.XENIUM_CTRLS` by default.
    additional_columns : collections.abc.Collection[str], optional
        Additional columns to load from the transcripts file.
    n_threads : int | None, optional
        Number of threads used for parsing the input file.
        If None, will default to number of available CPUs.

    Returns
    -------
    polars.DataFrame
    """
    filepath = Path(filepath)
    columns = list(set(_XENIUM_COLUMNS.keys()) | set(additional_columns))

    if filepath.suffix == ".parquet":
        transcripts = pl.scan_parquet(filepath)

        # 'is_gene' column only exists for Xenium v3 which only has .parquet
        if "is_gene" in transcripts.collect_schema().names():
            transcripts = transcripts.filter(pl.col("is_gene"))

        if min_qv is not None:
            transcripts = transcripts.filter(pl.col("qv") >= min_qv)

        with pl.StringCache():
            transcripts = (
                transcripts.select(columns)
                .with_columns(
                    pl.col("feature_name").cast(pl.String).cast(pl.Categorical)
                )
                .collect()
            )

    else:
        if min_qv is not None and "qv" not in additional_columns:
            columns.append("qv")
        transcripts = pl.read_csv(
            filepath,
            columns=columns,
            schema_overrides={"feature_name": pl.Categorical},
            n_threads=n_threads,
        )

        if min_qv is not None:
            transcripts = transcripts.filter(pl.col("qv") >= min_qv)
            if "qv" not in additional_columns:
                transcripts = transcripts.drop("qv")

    transcripts = transcripts.rename(_XENIUM_COLUMNS)
    transcripts = _filter_genes(transcripts, remove_features)

    return transcripts


# Vizgen MERSCOPE
_MERSCOPE_COLUMNS = {"gene": "gene", "global_x": "x", "global_y": "y", "global_z": "z"}

MERSCOPE_CTRLS = ["^Blank"]
"""Patterns for Vizgen controls"""


def read_MERSCOPE(
    filepath: str | os.PathLike,
    z_scale: float = 1.5,
    *,
    remove_genes: Collection[str] = MERSCOPE_CTRLS,
    additional_columns: Collection[str] = [],
    n_threads: int | None = None,
) -> pl.DataFrame:
    """
    Read a Vizgen transcripts file.

    Parameters
    ----------
    filepath : os.PathLike or str
        Path to the Vizgen transcripts file. Both, .csv(.gz) and .parquet files, are supported.
    z_scale : float
        Factor to scale z-plane index to um, i.e. distance between z-planes.
    remove_genes : collections.abc.Collection[str], optional
        List of regex patterns to filter the 'gene' column,
        :py:attr:`ovrlpy.io.MERSCOPE_CTRLS` by default.
    additional_columns : collections.abc.Collection[str], optional
        Additional columns to load from the transcripts file.
    n_threads : int | None, optional
        Number of threads used for parsing the input file.
        If None, will default to number of available CPUs.

    Returns
    -------
    polars.DataFrame
    """
    filepath = Path(filepath)
    columns = list(set(_MERSCOPE_COLUMNS.keys()) | set(additional_columns))

    if filepath.suffixes[-2:] == [".csv", ".gz"]:
        transcripts = pl.read_csv(
            filepath,
            columns=columns,
            schema_overrides={"gene": pl.Categorical},
            n_threads=n_threads,
        )

    else:
        if filepath.suffix == ".parquet":
            transcripts = pl.scan_parquet(filepath)
        elif filepath.suffix == ".csv":
            transcripts = pl.scan_csv(filepath)
        else:
            raise ValueError(
                "Unsupported file format; must be one of .csv(.gz) or .parquet"
            )

        with pl.StringCache():
            transcripts = (
                transcripts.select(columns)
                .with_columns(pl.col("gene").cast(pl.String).cast(pl.Categorical))
                .collect()
            )

    transcripts = transcripts.rename(_MERSCOPE_COLUMNS)
    transcripts = _filter_genes(transcripts, remove_genes)

    # convert plane to um
    transcripts = transcripts.with_columns(pl.col("z") * z_scale)

    return transcripts


# Nanostring CosMx
_COSMX_COLUMNS = {"target": "gene", "x_global_px": "x", "y_global_px": "y", "z": "z"}

COSMX_CTRLS = ["^NegPrb"]
"""Patterns for CosMx controls"""


def read_CosMx(
    filepath: str | os.PathLike,
    scale: Mapping[str, float] = {"xy": 0.12028, "z": 0.8},
    *,
    remove_targets: Collection[str] = COSMX_CTRLS,
    additional_columns: Collection[str] = [],
    n_threads: int | None = None,
) -> pl.DataFrame:
    """
    Read a Nanostring CosMx transcripts file.

    Parameters
    ----------
    filepath : os.PathLike or str
        Path to the CosMx transcripts file.
    scale : collections.abc.Mapping[str, float]
        The factors for scaling the coordinates from pixel space to um.
    remove_targets : collections.abc.Collection[str], optional
        List of regex patterns to filter the 'target' column,
        :py:attr:`ovrlpy.io.COSMX_CTRLS` by default.
    additional_columns : collections.abc.Collection[str], optional
        Additional columns to load from the transcripts file.
    n_threads : int | None, optional
        Number of threads used for parsing the input file.
        If None, will default to number of available CPUs.

    Returns
    -------
    polars.DataFrame
    """

    transcripts = pl.read_csv(
        Path(filepath),
        columns=list(set(_COSMX_COLUMNS.keys()) | set(additional_columns)),
        schema_overrides={"target": pl.Categorical},
        n_threads=n_threads,
    ).rename(_COSMX_COLUMNS)

    transcripts = _filter_genes(transcripts, remove_targets)

    # convert pixel to um
    transcripts = transcripts.with_columns(
        pl.col(["x", "y"]) * scale["xy"], pl.col("z") * scale["z"]
    )

    return transcripts
