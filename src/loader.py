from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
from zipfile import ZipFile

import pandas as pd


EXPECTED_COLUMNS = {"Ticker", "Date", "Price"}


def load_prices_from_zip(zip_path: str) -> pd.DataFrame:
    """Load and validate stock prices from the assignment ZIP archive.

    The real input contains one CSV per trading date with columns:
    Ticker, Date, Price.

    Each file contains exactly one row with a missing ticker. Those rows
    are dropped because they cannot identify a security. The remaining
    ticker universe must be identical across all files.
    """
    frames: list[pd.DataFrame] = []
    expected_tickers: set[str] | None = None

    with ZipFile(zip_path) as archive:
        csv_files = sorted(
            name
            for name in archive.namelist()
            if name.lower().endswith(".csv")
        )

        if not csv_files:
            raise ValueError("ZIP archive contains no CSV files.")

        for name in csv_files:
            with archive.open(name) as raw:
                frame = pd.read_csv(
                    BytesIO(raw.read()),
                    usecols=["Ticker", "Date", "Price"],
                )

            if set(frame.columns) != EXPECTED_COLUMNS:
                raise ValueError(
                    f"{name}: expected columns "
                    f"{sorted(EXPECTED_COLUMNS)}, got {list(frame.columns)}"
                )

            frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
            frame["Price"] = pd.to_numeric(frame["Price"], errors="coerce")

            if frame["Date"].isna().any():
                raise ValueError(f"{name}: invalid dates found.")

            if (frame["Price"] <= 0).any():
                raise ValueError(f"{name}: non-positive prices found.")

            missing_ticker = frame["Ticker"].isna()
            if missing_ticker.sum() != 1:
                raise ValueError(
                    f"{name}: expected exactly one missing ticker, "
                    f"found {int(missing_ticker.sum())}."
                )

            frame = frame.loc[~missing_ticker].copy()
            frame["Ticker"] = frame["Ticker"].astype(str)

            if frame["Ticker"].duplicated().any():
                raise ValueError(f"{name}: duplicate tickers found.")

            tickers = set(frame["Ticker"])

            if expected_tickers is None:
                expected_tickers = tickers
            elif tickers != expected_tickers:
                missing = expected_tickers - tickers
                extra = tickers - expected_tickers
                raise ValueError(
                    f"{name}: ticker universe changed. "
                    f"Missing={sorted(missing)[:5]}, "
                    f"Extra={sorted(extra)[:5]}"
                )

            frames.append(frame)

    data = pd.concat(frames, ignore_index=True)

    data = data.rename(
        columns={
            "Ticker": "ticker",
            "Date": "date",
            "Price": "price",
        }
    )

    data["ticker"] = data["ticker"].astype("category")
    data["price"] = data["price"].astype("float32")

    data = data.sort_values(["date", "ticker"]).reset_index(drop=True)

    if data.duplicated(["date", "ticker"]).any():
        raise ValueError("Duplicate date/ticker observations remain after loading.")

    return data


def build_price_matrix(data: pd.DataFrame) -> pd.DataFrame:
    """Convert tidy prices into a date x ticker price matrix."""
    return (
        data.pivot(index="date", columns="ticker", values="price")
        .sort_index()
    )

def load_prices(input_path: str | Path) -> pd.DataFrame:
    """Backward-compatible entry point for the existing pipeline/tests."""
    return load_prices_from_zip(str(input_path))
def load_prices(input_path: str | Path) -> pd.DataFrame:
    """Load prices from either the assignment ZIP or a directory of CSVs."""
    path = Path(input_path)

    if path.is_dir():
        frames: list[pd.DataFrame] = []

        for csv_path in sorted(path.rglob("*.csv")):
            raw = pd.read_csv(csv_path)

            # Support the lightweight CSV format used by unit tests.
            if {"ticker", "close"}.issubset(raw.columns):
                frame = raw[["ticker", "close"]].copy()
                frame["date"] = _date_from_filename(csv_path.name)
                frame["ticker"] = frame["ticker"].astype(str).str.strip()
                frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
                frame = frame.dropna(subset=["ticker", "close"])
                frames.append(frame[["date", "ticker", "close"]])
            else:
                frames.append(
                    normalize_daily_csv(raw, csv_path.name)
                )

        if not frames:
            raise ValueError("No CSV files found.")

        data = pd.concat(frames, ignore_index=True)
        data = data.sort_values(["date", "ticker"]).reset_index(drop=True)

        if data.duplicated(["date", "ticker"]).any():
            raise ValueError(
                "Duplicate date/ticker observations remain after loading."
            )

        return data

    if path.suffix.lower() == ".zip":
        return load_prices_from_zip(str(path))

    raise ValueError(
        "Input must be a directory containing CSV files or a .zip file."
    )

def _date_from_filename(name: str) -> pd.Timestamp:
    """Extract a YYYYMMDD date from a CSV filename."""
    match = re.search(r"(20\d{6})", Path(name).name)
    if not match:
        raise ValueError(f"Could not infer YYYYMMDD date from filename: {name}")
    return pd.to_datetime(match.group(1), format="%Y%m%d")
