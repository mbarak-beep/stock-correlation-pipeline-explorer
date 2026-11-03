from __future__ import annotations

import numpy as np
import pandas as pd


def correlation_matrix(window: pd.DataFrame) -> np.ndarray:
    """Calculate Pearson correlations using complete 20-return windows.

    Assets with missing returns or constant returns receive NaN
    correlations. No missing values are imputed.
    """
    if window.shape[0] < 2:
        raise ValueError("At least two observations are required.")

    values = window.to_numpy(dtype=np.float32, copy=False)

    # Only assets with a complete return window can participate.
    complete = np.isfinite(values).all(axis=0)

    correlation = np.full(
        (values.shape[1], values.shape[1]),
        np.nan,
        dtype=np.float32,
    )

    if complete.sum() < 2:
        return correlation

    complete_values = values[:, complete]
    centered = complete_values - complete_values.mean(axis=0, keepdims=True)
    std = centered.std(axis=0, ddof=1)

    # Constant return series have undefined Pearson correlations.
    non_constant = std > 0

    if non_constant.sum() < 2:
        return correlation

    standardized = centered[:, non_constant] / std[non_constant]

    valid_correlation = (
        standardized.T @ standardized
    ) / np.float32(values.shape[0] - 1)

    valid_indices = np.flatnonzero(complete)[non_constant]

    correlation[np.ix_(valid_indices, valid_indices)] = (
        valid_correlation.astype(np.float32, copy=False)
    )

    np.clip(correlation, -1.0, 1.0, out=correlation)

    correlation[valid_indices, valid_indices] = 1.0

    return correlation


def upper_triangle(matrix: np.ndarray):
    """Return the strict upper triangle of a square matrix."""
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Correlation matrix must be square.")

    rows, cols = np.triu_indices(matrix.shape[0], k=1)
    return rows, cols, matrix[rows, cols]
