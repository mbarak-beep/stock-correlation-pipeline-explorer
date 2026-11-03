from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def save_correlation(
    output_dir: str | Path,
    date: pd.Timestamp,
    matrix: np.ndarray,
) -> Path:
    """Store a symmetric correlation matrix using only its upper triangle."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    matrix = np.asarray(matrix, dtype=np.float32)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Correlation matrix must be square.")

    n_assets = matrix.shape[0]
    rows, cols = np.triu_indices(n_assets, k=1)
    values = matrix[rows, cols]

    return save_upper_triangle(
        output_dir=output,
        date=date,
        rows=rows,
        cols=cols,
        values=values,
        n_assets=n_assets,
        diagonal=np.diag(matrix).copy(),
    )


def save_upper_triangle(
    output_dir: str | Path,
    date: pd.Timestamp,
    rows: np.ndarray,
    cols: np.ndarray,
    values: np.ndarray,
    n_assets: int,
    diagonal: np.ndarray | None = None,
) -> Path:
    """Store upper-triangle values and the original matrix diagonal."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    rows = np.asarray(rows, dtype=np.int32)
    cols = np.asarray(cols, dtype=np.int32)
    values = np.asarray(values, dtype=np.float32)

    expected_pairs = n_assets * (n_assets - 1) // 2

    if len(rows) != expected_pairs or len(cols) != expected_pairs:
        raise ValueError("Incorrect number of upper-triangle indices.")

    if len(values) != expected_pairs:
        raise ValueError("Incorrect number of correlation values.")

    expected_rows, expected_cols = np.triu_indices(n_assets, k=1)

    if not (
        np.array_equal(rows, expected_rows)
        and np.array_equal(cols, expected_cols)
    ):
        raise ValueError("Upper-triangle indices must use canonical ordering.")

    filename = pd.Timestamp(date).strftime("%Y%m%d") + ".npz"
    path = output / filename

    if diagonal is None:
        diagonal = np.ones(n_assets, dtype=np.float32)
    else:
        diagonal = np.asarray(diagonal, dtype=np.float32)

    if diagonal.shape != (n_assets,):
        raise ValueError("Diagonal must contain one value per asset.")

    np.savez_compressed(
        path,
        values=values,
        n_assets=np.int32(n_assets),
        diagonal=diagonal,
    )

    return path


def load_upper_triangle(
    output_dir: str | Path,
    date: pd.Timestamp,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Load correlation values and reconstruct deterministic indices."""
    output = Path(output_dir)
    filename = pd.Timestamp(date).strftime("%Y%m%d") + ".npz"
    path = output / filename

    if not path.exists():
        raise FileNotFoundError(f"No correlation data for {date}: {path}")

    with np.load(path) as data:
        values = data["values"]
        n_assets = int(data["n_assets"])

    expected_pairs = n_assets * (n_assets - 1) // 2

    if len(values) != expected_pairs:
        raise ValueError(f"Corrupt or incomplete correlation file: {path}")

    rows, cols = np.triu_indices(n_assets, k=1)

    return rows, cols, values, n_assets


def load_correlation(
    output_dir: str | Path,
    date: pd.Timestamp,
) -> np.ndarray:
    """Load a stored correlation matrix and reconstruct its symmetry."""
    rows, cols, values, n_assets = load_upper_triangle(
        output_dir,
        date,
    )

    matrix = np.empty((n_assets, n_assets), dtype=np.float32)
    matrix.fill(np.nan)
    matrix[rows, cols] = values
    matrix[cols, rows] = values

    path = (
        Path(output_dir)
        / (pd.Timestamp(date).strftime("%Y%m%d") + ".npz")
    )
    with np.load(path) as data:
        if "diagonal" in data.files:
            diagonal = data["diagonal"]
        else:
            diagonal = np.ones(n_assets, dtype=np.float32)

    if diagonal.shape != (n_assets,):
        raise ValueError(f"Invalid diagonal in correlation file: {path}")

    np.fill_diagonal(matrix, diagonal)
    return matrix


def reconstruct_matrix(
    output_dir: str | Path,
    date: pd.Timestamp,
) -> np.ndarray:
    """Alias for load_correlation."""
    return load_correlation(output_dir, date)


def save_metadata(
    output_dir: str | Path,
    tickers: list[str],
) -> Path:
    """Store the ticker-to-matrix-index mapping."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    metadata = pd.DataFrame(
        {
            "ticker": tickers,
            "index": np.arange(len(tickers), dtype=np.int32),
        }
    )

    path = output / "tickers.parquet"
    metadata.to_parquet(path, index=False)

    return path


def save_tickers(
    output_dir: str | Path,
    tickers: pd.DataFrame,
) -> Path:
    """Store an existing ticker metadata DataFrame."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    path = output / "tickers.parquet"
    tickers.to_parquet(path, index=False)

    return path


def load_tickers(output_dir: str | Path) -> pd.DataFrame:
    """Load the ticker-to-matrix-index mapping."""
    return pd.read_parquet(Path(output_dir) / "tickers.parquet")


def available_dates(output_dir: str | Path) -> list[pd.Timestamp]:
    """Return dates for which correlation files exist."""
    output = Path(output_dir)
    dates: list[pd.Timestamp] = []

    metadata_path = output / "tickers.parquet"
    if not metadata_path.exists():
        return dates

    n_assets = len(pd.read_parquet(metadata_path))
    expected_pairs = n_assets * (n_assets - 1) // 2

    for path in sorted(output.glob("*.npz")):
        try:
            date = pd.to_datetime(path.stem, format="%Y%m%d")

            with np.load(path) as data:
                values = data["values"]
                stored_assets = int(data["n_assets"])

            if stored_assets != n_assets or len(values) != expected_pairs:
                continue

            dates.append(date)

        except (ValueError, KeyError, OSError, EOFError):
            continue

    return dates
