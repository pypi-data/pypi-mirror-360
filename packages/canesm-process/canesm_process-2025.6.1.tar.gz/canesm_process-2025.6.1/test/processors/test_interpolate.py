import numpy as np
from canproc.processors.interpolate import fast_linear_interp


def test_fast_linear_interp_extend():

    xp = np.arange(10, 91, 1.0, dtype=np.float32)
    fp = xp**2
    x = np.arange(0.0, 101.0, 1.0, dtype=np.float32)
    f = np.zeros_like(x)

    true_f = np.interp(x, xp, fp)
    fast_linear_interp(x, xp, fp, f)

    np.testing.assert_allclose(true_f, f)


def test_fast_linear_interp_midpoints():

    xp = np.arange(10, 91, 1.0, dtype=np.float32)
    fp = xp**2
    x = np.arange(10.25, 91, 1.0, dtype=np.float32)
    f = np.zeros_like(x)

    true_f = np.interp(x, xp, fp)
    fast_linear_interp(x, xp, fp, f)

    np.testing.assert_allclose(true_f, f)


def test_fast_linear_interp_low_to_high():

    xp = np.arange(10, 91, 1.0, dtype=np.float32)
    fp = xp**2
    x = np.linspace(10.25, 91, 300, dtype=np.float32)
    f = np.zeros_like(x)

    true_f = np.interp(x, xp, fp)
    fast_linear_interp(x, xp, fp, f)

    np.testing.assert_allclose(true_f, f)


def test_fast_linear_interp_high_to_low():

    xp = np.linspace(10, 91, 100, dtype=np.float32)
    fp = xp**2
    x = np.linspace(10.25, 91, 10, dtype=np.float32)
    f = np.zeros_like(x)

    true_f = np.interp(x, xp, fp)
    fast_linear_interp(x, xp, fp, f)

    np.testing.assert_allclose(true_f, f)
