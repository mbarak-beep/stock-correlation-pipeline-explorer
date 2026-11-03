from __future__ import annotations

import numpy as np
import pandas as pd


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate simple daily percentage returns."""
    if prices.empty:
        raise ValueError("prices must not be empty")

    prices = prices.sort_index()

    if not prices.index.is_unique:
        raise ValueError("Price index must contain unique dates.")

    if (prices <= 0).any().any():
        raise ValueError("Prices must be strictly positive.")

    returns = prices.pct_change(fill_method=None)

    return returns


def trailing_return_window(
    returns: pd.DataFrame,
    end_position: int,
    window: int = 20,
) -> pd.DataFrame:
    """Return exactly window returns ending at end_position.

    A 20-return window corresponds to 21 underlying price observations.
    """
    if window < 2:
        raise ValueError("window must be at least 2")

    if end_position < 0 or end_position >= len(returns):
        raise IndexError("end_position is outside the returns DataFrame")

    start = end_position - window + 1

    if start < 0:
        raise ValueError(
            f"Not enough observations for a {window}-return window."
        )

    result = returns.iloc[start : end_position + 1]

    if len(result) != window:
        raise RuntimeError(
            f"Expected {window} returns, got {len(result)}."
        )

    return result


def eligible_end_positions(
    returns: pd.DataFrame,
    window: int = 20,
) -> range:
    """Return positions where a complete trailing return window exists."""
    if window < 2:
        raise ValueError("window must be at least 2")

    # The first row of pct_change() is the initial NaN and is not
    # an actual return observation.
    first_valid_position = 1

    if len(returns) <= first_valid_position:
        return range(0)

    first_end_position = first_valid_position + window - 1

    if first_end_position >= len(returns):
        return range(0)

    return range(first_end_position, len(returns))
