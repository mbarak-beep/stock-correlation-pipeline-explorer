import numpy as np
import pandas as pd

from src.returns import daily_returns, trailing_return_window


def test_daily_returns():
    prices = pd.DataFrame({"A": [100.0, 110.0, 121.0]})
    result = daily_returns(prices)

    assert np.isnan(result["A"].iloc[0])
    assert np.isclose(result["A"].iloc[1], 0.10)
    assert np.isclose(result["A"].iloc[2], 0.10)


def test_trailing_window():
    returns = pd.DataFrame({"A": range(5)})
    result = trailing_return_window(returns, end_position=4, window=3)
    assert result["A"].tolist() == [2, 3, 4]
