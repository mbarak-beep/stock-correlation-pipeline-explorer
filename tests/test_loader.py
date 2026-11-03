from pathlib import Path
import pandas as pd

from src.loader import load_prices


def test_load_prices_from_directory(tmp_path: Path):
    csv = tmp_path / "20200101.csv"
    pd.DataFrame({"ticker": ["A", "B"], "close": [100.0, 200.0]}).to_csv(
        csv, index=False
    )

    result = load_prices(tmp_path)

    assert list(result.columns) == ["date", "ticker", "close"]
    assert len(result) == 2
    assert result["date"].iloc[0] == pd.Timestamp("2020-01-01")
