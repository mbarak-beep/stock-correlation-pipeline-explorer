import numpy as np
import pandas as pd

from src.correlation import correlation_matrix, upper_triangle


def test_perfect_positive_correlation():
    window = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [2, 4, 6, 8, 10]})
    corr = correlation_matrix(window)

    assert np.isclose(corr[0, 0], 1.0)
    assert np.isclose(corr[1, 1], 1.0)
    assert np.isclose(corr[0, 1], 1.0)


def test_perfect_negative_correlation():
    window = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [10, 8, 6, 4, 2]})
    corr = correlation_matrix(window)
    assert np.isclose(corr[0, 1], -1.0)


def test_upper_triangle():
    matrix = np.eye(3, dtype=np.float32)
    matrix[0, 1] = matrix[1, 0] = 0.5
    matrix[0, 2] = matrix[2, 0] = -0.2
    matrix[1, 2] = matrix[2, 1] = 0.7

    rows, cols, values = upper_triangle(matrix)

    assert list(zip(rows, cols)) == [(0, 1), (0, 2), (1, 2)]
    assert np.allclose(values, [0.5, -0.2, 0.7])
