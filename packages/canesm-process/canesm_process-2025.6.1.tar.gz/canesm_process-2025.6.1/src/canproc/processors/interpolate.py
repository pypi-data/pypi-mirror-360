import numpy as np
from numba import njit
from typing import Callable, Literal


@njit
def fast_linear_interp(x: np.ndarray, xp: np.ndarray, fp: np.ndarray, out: np.ndarray):
    """
    Performs a 1D linear interpolation of values in `x` based on known data points (`xp`, `fp`).
    Roughly equivalent to `numpy.interp(...)` with in-place interpolation.

    Parameters
    ----------
    x : np.ndarray
        The x-coordinates at which to evaluate the interpolated values, must be increasing.
    xp : np.ndarray
        The x-coordinates of the data points, must be increasing.
    fp : np.ndarray
        The y-coordinates of the data points, same length as `xp`.
    out : np.ndarray
        The output array to store the interpolated values. Must be the same shape as `x`.

    Returns
    -------
    None
        The result is stored in the `out` array in-place.

    Notes
    -----
     - Useful when interpolating large matrices to avoid np.interp overhead.
     - scipy.interp1d doesn't support varying coordinates along the interpolation dimension for ND arrays.

    """

    xp_index = 0
    x_index = 0
    lastx = xp[xp.size - 1]
    lastf = fp[fp.size - 1]

    # set anything less than the lower bound of x
    for x_index in range(x_index, x.size):
        if xp[0] < x[x_index]:
            break
        else:
            out[x_index] = fp[0]

    for x_index in range(x_index, x.size):
        # set anything above the upper bound of x
        if x[x_index] >= lastx:
            out[x_index] = lastf

        # find the next index above the current xp value
        else:
            while xp_index < xp.size:
                if x[x_index] == xp[xp_index]:
                    out[x_index] = fp[xp_index]
                    break
                elif x[x_index] < xp[xp_index]:
                    out[x_index] = fp[xp_index - 1] + (
                        (x[x_index] - xp[xp_index - 1]) / (xp[xp_index] - xp[xp_index - 1])
                    ) * (fp[xp_index] - fp[xp_index - 1])
                    break
                xp_index += 1


####################################################################################
# Wrappers for `fast_linear_interp` used for dispatch of different array ranks.
# This is needed as numba parameters cannot have dynamic rank
####################################################################################
@njit
def interpolate_ndarray_1d(x: np.ndarray, xp: np.ndarray, fp: np.ndarray, interpolator: Callable):
    output = np.zeros(x.size, dtype=fp.dtype)
    interpolator(x, xp, fp, output)
    return output


@njit
def interpolate_ndarray_2d(x: np.ndarray, xp: np.ndarray, fp: np.ndarray, interpolator: Callable):
    output = np.zeros((fp.shape[0], x.size), dtype=fp.dtype)
    for i in range(fp.shape[0]):
        interpolator(x, xp[i, :], fp[i, :], output[i, :])
    return output


@njit
def interpolate_ndarray_3d(x: np.ndarray, xp: np.ndarray, fp: np.ndarray, interpolator: Callable):
    output = np.zeros((fp.shape[0], fp.shape[1], x.size), dtype=fp.dtype)
    for i in range(fp.shape[0]):
        for j in range(fp.shape[1]):
            interpolator(x, xp[i, j, :], fp[i, j, :], output[i, j, :])
    return output


@njit
def interpolate_ndarray_4d(x: np.ndarray, xp: np.ndarray, fp: np.ndarray, interpolator: Callable):
    output = np.zeros((fp.shape[0], fp.shape[1], fp.shape[2], x.size), dtype=fp.dtype)
    for i in range(fp.shape[0]):
        for j in range(fp.shape[1]):
            for k in range(fp.shape[2]):
                interpolator(x, xp[i, j, k, :], fp[i, j, k, :], output[i, j, k, :])
    return output


def interpolate_ndarray(
    x: np.ndarray, xp: np.ndarray, fp: np.ndarray, kind: Literal["linear"] = "linear"
):
    """
    Interpolate ND array, `fp` with a variable `xp` dimension onto a common `x` grid.

    Parameters
    ----------
    x: np.ndarray
        1D array defining the output grid
    xp: nd.ndarray
        ND array defining the x coordinate of the input grid
    fp: nd.ndarray
        ND array data on the input grid. Must be the same size as xp
    kind: Literal["linear'], optional
        interpolation method to use. linear by default.

    Returns
    -------
    np.ndarray:
        `fp` interpolated on `x`
    """

    if xp.shape != fp.shape:
        raise ValueError("shape of xp and fp must be equal")

    if len(x.shape) != 1:
        raise ValueError("output grid must be one dimensional")

    if kind == "linear":
        interp = fast_linear_interp  # must be an njit compiled function?
    else:
        raise ValueError("only linear interpolation is currently supported")

    # dispatch to appropriate njit function
    if len(fp.shape) == 1:
        return interpolate_ndarray_1d(x, xp, fp, interp)
    elif len(fp.shape) == 2:
        return interpolate_ndarray_2d(x, xp, fp, interp)
    elif len(fp.shape) == 3:
        return interpolate_ndarray_3d(x, xp, fp, interp)
    elif len(fp.shape) == 4:
        return interpolate_ndarray_4d(x, xp, fp, interp)
