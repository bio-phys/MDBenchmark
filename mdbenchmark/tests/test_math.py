import numpy as np
from numpy.testing import assert_equal

from mdbenchmark import math


def test_lin_func():
    """Test `lin_func()`."""
    m, x, b = [5, 3, 2]

    assert_equal(math.lin_func(m, x, b), (m * x) + b)


def test_calc_slope_intercept():
    """Test `calc_slope_intercept()`"""
    x1, y1 = [1, 1]
    x2, y2 = [2, 2]
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (x1 * slope)

    slope_intercept = math.calc_slope_intercept((x1, y1), (x2, y2))

    assert_equal(slope_intercept, np.hstack([slope, intercept]))
