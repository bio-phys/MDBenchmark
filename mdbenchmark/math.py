import numpy as np


def lin_func(x, m, b):
    return m * x + b


def calc_slope_intercept(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    diff = x - y
    slope = diff[1] / diff[0]
    intercept = x[1] - (x[0] * slope)
    return np.hstack([slope, intercept])
