import numpy as np
import pandas as pd

from src.storage import (
    save_correlation,
    load_correlation,
    save_metadata,
    load_tickers,
    available_dates,
)


def test_storage_round_trip(tmp_path):
    matrix = np.array(
        [[1.0, 0.5, -0.2], [0.5, 1.0, 0.7], [-0.2, 0.7, 1.0]],
        dtype=np.float32,
    )

    date = pd.Timestamp("2020-01-31")
    save_correlation(tmp_path, date, matrix)
    result = load_correlation(tmp_path, date)

    assert np.allclose(result, matrix)


def test_storage_preserves_nan_diagonal(tmp_path):
    matrix = np.array(
        [
            [1.0, 0.5, np.nan],
            [0.5, 1.0, np.nan],
            [np.nan, np.nan, np.nan],
        ],
        dtype=np.float32,
    )

    date = pd.Timestamp("2020-02-03")
    save_correlation(tmp_path, date, matrix)
    result = load_correlation(tmp_path, date)

    assert np.allclose(result, matrix, equal_nan=True)
    assert np.isnan(result[2]).all()


def test_metadata_and_dates(tmp_path):
    save_metadata(tmp_path, ["A", "B", "C"])
    assert load_tickers(tmp_path)["ticker"].tolist() == ["A", "B", "C"]

    save_correlation(
        tmp_path,
        pd.Timestamp("2020-01-31"),
        np.eye(3, dtype=np.float32),
    )
    assert available_dates(tmp_path) == [pd.Timestamp("2020-01-31")]


def test_available_dates_excludes_incomplete_files(tmp_path):
    save_metadata(tmp_path, ["A", "B", "C"])

    valid_date = pd.Timestamp("2020-01-31")
    save_correlation(tmp_path, valid_date, np.eye(3, dtype=np.float32))

    incomplete_path = tmp_path / "20200203.npz"
    np.savez_compressed(
        incomplete_path,
        values=np.array([0.5], dtype=np.float32),
        n_assets=np.int32(3),
    )

    assert available_dates(tmp_path) == [valid_date]
