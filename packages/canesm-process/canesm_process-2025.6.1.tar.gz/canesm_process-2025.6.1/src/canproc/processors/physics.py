import numpy as np
from scipy.interpolate import interp1d
import xarray as xr
from canproc.processors.interpolate import interpolate_ndarray, fast_linear_interp
from canproc.processors.xarray_ops import to_array, to_dataset

g_over_R = 0.034163043478260866  # gravity / gas_constant = 9.80616/287.04


def interpolate_pressure_to_altitude_hypsometric_ndarray(
    geopotential_height: np.ndarray,
    temperature: np.ndarray,
    plev: np.ndarray,
    altitude: np.ndarray,
):
    """Compute the pressure at altitude levels useing the hypsometric equation

    Parameters
    ----------
    geopotential_height : np.ndarray
        geopotential height in meters. Should be strictly increasing.
    temperature : np.ndarray
        temperature in kelvin
    plev : np.ndarray
        pressure levels corresonding to geopotential and temperature arrays
    altitude : np.ndarray
        output altitude grid in meters

    Returns
    -------
    np.ndarray
        1D array of pressure at altitude
    """

    # get the temperature at the altitudes of interest
    # temp_on_alt = np.interp(altitude, geopotential_height, temperature)
    temp_on_alt = interp1d(geopotential_height, temperature, kind="cubic")(altitude)

    # index of zg just below altitude
    # TODO: better to use the nearest?
    idx = np.digitize(altitude, geopotential_height) - 1

    return plev[idx] * np.exp(
        g_over_R / ((temperature[idx] + temp_on_alt) / 2) * (geopotential_height[idx] - altitude)
    )


def interpolate_pressure_to_altitude_hypsometric(
    geopotential_height: xr.DataArray, temperature: xr.DataArray, altitude: xr.DataArray
) -> xr.DataArray:
    """Interpolate pressure at a given altitude using the hypsometric equation

    Parameters
    ----------
    geopotential_height : xr.DataArray
        geopotential height [m], must not be chunked along altitude
    temperature : xr.DataArray
        temperature [k], must not be chunked along altitude
    altitude : xr.DataArray
        altitude [m]

    Returns
    -------
    xr.DataArray
        pressure at altitude levels
    """

    # TODO: avoid load call - required for now since data isn't chunked by altitude so single altitudes are passed without load.
    return xr.apply_ufunc(
        interpolate_pressure_to_altitude_hypsometric_ndarray,
        geopotential_height,
        temperature,
        geopotential_height.plev,
        altitude,
        input_core_dims=[["plev"], ["plev"], ["plev"], ["altitude"]],
        output_core_dims=[["altitude"]],
        vectorize=True,
        dask="parallelized",
        dask_gufunc_kwargs={"allow_rechunk": True},
    )


def log_hybrid_sigma_to_pressure(surface_pressure, a, b, p_ref):
    return np.exp(a) * ((surface_pressure / p_ref) ** b)


def interpolate_to_pressure(
    data: xr.DataArray,
    input_pressure: xr.DataArray,
    output_pressure: xr.DataArray | list[float] | np.ndarray,
    input_dim: str = "level",
    output_dim: str = "plev",
) -> xr.DataArray:
    """Interpolate data on log hybrid sigma levels [0, 1] onto pressure

    Parameters
    ----------
    data: xr.DataArray
        Data to be interpolated
    input_pressure: xr.DataArray
        Pressure used for interpolation, should be the same shape as `data`
    output_pressure: xr.DataArray
        One dimensional output pressure levels

    Returns
    -------
    xr.DataArray
        data interpolated onto pressure levels
    """

    if isinstance(output_pressure, list) or isinstance(output_pressure, np.ndarray):
        output_pressure = xr.DataArray(output_pressure, coords=[output_pressure], dims=[output_dim])

    # convert dataset to array to avoid problems with non-matching names
    is_dataset = isinstance(data, xr.Dataset)
    if is_dataset:
        data = to_array(data)
        name = data.name

    ds = xr.apply_ufunc(
        interpolate_ndarray,
        np.log(output_pressure),
        to_array(np.log(input_pressure)),
        data,
        input_core_dims=[[output_dim], [input_dim], [input_dim]],
        output_core_dims=[[output_dim]],
        dask="parallelized",
        dask_gufunc_kwargs={"allow_rechunk": True},
    )

    if is_dataset:
        return to_dataset(ds.rename(name))

    return ds


def planck(wavelength: float | np.ndarray, temperature: float):
    """compute the planck function at a given wavelength [m] and temperature [K]

    Parameters
    ----------
    wavelength : float | np.ndarray
        wavelength in meters
    temperature : float
        blackbody temperature in kelvin.

    Returns
    -------
    float | np.ndarray
    """
    h = 6.626070156e-34  # Js
    c = 299792458.0  # m/s
    k = 1.380649e-23  # J

    a = 2 * h * c**2
    b = h * c / (wavelength * k * temperature)
    return a / ((wavelength**5) * (np.exp(b) - 1))


def wavenumber_to_wavelength(wavenumber):
    return 1e7 / wavenumber
