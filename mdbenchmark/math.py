import numpy as np


def lin_func(x, m, b):
    return m * x + b


def calc_slope_intercept(p1, p2):
    p1 = np.asarray(p1)
    p2 = np.asarray(p2)
    diff = p1 - p2
    slope = diff[1] / diff[0]
    intercept = p1[1] - (p1[0] * slope)
    return np.hstack([slope, intercept])
