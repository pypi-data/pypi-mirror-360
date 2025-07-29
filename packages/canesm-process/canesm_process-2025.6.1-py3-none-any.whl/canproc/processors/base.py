import xarray as xr
import numpy as np
import logging
from datetime import datetime
from canproc.processors.xarray_ops import to_array, to_dataset
import canproc
from typing import Callable, Literal
from pathlib import Path


def open_mfdataset(*args, **kwargs):

    try:
        return xr.open_mfdataset(*args, **kwargs)
    except Exception as e:
        logging.error(e)
        raise e
    #  return xr.open_dataset(*args)


def to_netcdf(
    data: xr.Dataset | xr.DataArray, filename: str, **kwargs
) -> xr.Dataset | xr.DataArray:
    """
    Save an xarray Dataset or DataArray to a NetCDF file with CMIP-compliant options.

    This function wraps `xarray.to_netcdf`, providing additional handling for encoding options
    (such as writing double-precision floats as single-precision) and metadata insertion.
    It also appends provenance information to the dataset attributes.

    Parameters
    ----------
    data : xr.Dataset or xr.DataArray
        The xarray object to be saved.
    filename : str
        The path to the output NetCDF file.
    **kwargs
        Additional keyword arguments passed to `xarray.to_netcdf`. Special handling is provided for:
            - encoding: dict, optional
                Encoding options for variables. If 'write_double_as_float' is present, float64 variables
                are written as float32.
            - metadata: dict, optional
                Metadata to be added to the dataset before saving.

    Returns
    -------
    xr.Dataset or xr.DataArray
        The input data, possibly with updated attributes.
    """

    if "encoding" in kwargs:
        if "write_double_as_float" in kwargs["encoding"]:
            for var in data.data_vars:
                enc = kwargs["encoding"]
                enc["dtype"] = (
                    "float32" if isinstance(data[var].dtype, np.float64) else data[var].dtype
                )
                kwargs["encoding"] = {var: enc}
        else:
            kwargs["encoding"] = {var: kwargs["encoding"] for var in data.data_vars}

    if "metadata" in kwargs:
        md = kwargs.pop("metadata")
        data = add_metadata(data, md)
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data.attrs["info"] = (
        f"File produced using canesm-processor version {canproc.__version__} on {dt}."
    )

    return data.to_netcdf(filename, **kwargs)


def add_metadata(data, metadata):
    for var in data.data_vars:
        for key in metadata.keys():
            if key == "min" and metadata["min"]:
                data[var].attrs["min"] = data[var].values.min()
            elif key == "max" and metadata["max"]:
                data[var].attrs["max"] = data[var].values.max()
            else:
                data[var].attrs[key] = metadata[key]
    return data


def select_region(
    data: xr.Dataset | xr.DataArray,
    region: dict[str, tuple[float, float]] = {"lat": (-90, 90), "lon": (-180, 360)},
) -> xr.Dataset | xr.DataArray:
    """
    Select a geopraphic region. Expects longitude coordinates (0 to 360).
    If longitude[1] > longitude[0] selection is wrapped from east to west.

    Parameters
    ----------
    data : xr.Dataset | xr.DataArray
        input data
    region : dict[str, tuple[float, float]], optional
        region to use for selection, by default {"lat": (-90, 90), "lon": (-180, 360)}

    Returns
    -------
    xr.Dataset | xr.DataArray
        subset of input data
    """

    latdim, londim = list(region.keys())

    min_longitude = region[londim][0]
    max_longitude = region[londim][1]
    min_latitude = region[latdim][0]
    max_latitude = region[latdim][1]

    if data[londim].max() > 180:
        if not region == {"lat": (-90, 90), "lon": (-180, 360)}:
            if max_longitude < 0:
                max_longitude += 360
            if min_longitude < 0:
                min_longitude += 360
            # raise ValueError(f"only (-180 to 180) longitude values are supported {data[londim].max()}")

    if region:
        if min_longitude > max_longitude:
            d1 = data.sel({londim: slice(min_longitude, 360)})
            d2 = data.sel({londim: slice(-180, max_longitude)})
            data = xr.concat([d2, d1], dim=londim)
        else:
            data = data.sel(lon=slice(min_longitude, max_longitude))
        data = data.sel({latdim: slice(min_latitude, max_latitude)})

    return data


def spherical_weights(lat_bnds: np.ndarray) -> np.ndarray:
    """
    Calculates the area weights for latitude bands on a sphere using their boundaries.

    Parameters
    ----------
    lat_bnds : np.ndarray
        Array of latitude boundaries in degrees. Can be either:
        - 1D array of shape (N+1,) representing N latitude bands, or
        - 2D array of shape (M, 2) where each row contains the lower and upper latitude bounds of a band.

    Returns
    -------
    np.ndarray
        Array of weights corresponding to each latitude band, representing the fractional area of the sphere covered by each band.

    Notes
    -----
    The weights are computed as the difference in the sine of the latitude boundaries (converted to radians), which corresponds to the area between two latitudes on a unit sphere.
    """
    if len(lat_bnds.shape) == 1:
        return np.sin(lat_bnds[1:] * np.pi / 180) - np.sin(lat_bnds[0:-1] * np.pi / 180)
    else:
        return np.sin(lat_bnds[:, 1] * np.pi / 180) - np.sin(lat_bnds[:, 0] * np.pi / 180)


def linear_weights(bnds: np.ndarray) -> np.ndarray:
    """
    Calculates linear weights from boundary values.

    Parameters
    ----------
    bnds : np.ndarray
        An array of boundary values. Can be either 1-dimensional or 2-dimensional.
        - If 1D, the weights are computed as the difference between consecutive elements.
        - If 2D, the weights are computed as the difference between the second and first column for each row.

    Returns
    -------
    np.ndarray
        An array of weights calculated from the input boundaries. The shape depends on the input:
        - For 1D input: shape is (len(bnds) - 1,)
        - For 2D input: shape is (bnds.shape[0],)

    Examples
    --------
    >>> linear_weights(np.array([0, 1, 3]))
    array([1, 2])

    >>> linear_weights(np.array([[0, 1], [1, 3]]))
    array([1, 2])
    """
    if len(bnds.shape) == 1:
        return bnds[1:] - bnds[0:-1]
    else:
        return bnds[:, 1] - bnds[:, 0]


def area_weights(
    data: xr.DataArray | xr.Dataset, latdim: str = "lat", kernel: Callable = spherical_weights
) -> xr.DataArray:
    """
    Compute the relative weights for area weighting. Input data is expected to be on a regular grid.

    Parameters
    ----------
    data : xr.DataArray | xr.Dataset
        Input data
    latdim : str, optional
        name of latitude dimension, by default `lat`
    kernel : Callable, optional
        function to compute the weights, by default spherical_area

    Returns
    -------
    xr.DataArray
        weights along the `latdim` dimension
    """
    lat_bnds = None
    if isinstance(data, xr.Dataset):
        try:
            lat_bnds = data[f"{latdim}_bnds"].squeeze().to_numpy()
        except KeyError:
            pass

    if lat_bnds is None:
        lats = data[latdim].to_numpy()
        lat_diff = np.diff(lats)
        lat_bnds = np.concatenate(
            [[lats[0] - lat_diff[0] / 2], lats[0:-1] + lat_diff / 2, [lats[-1] + lat_diff[1] / 2]]
        )

    return xr.DataArray(kernel(lat_bnds), coords=[data[latdim].to_numpy()], dims=[latdim])


def cell_area(
    data: xr.DataArray | xr.Dataset,
    latdim: str = "lat",
    londim: str = "lon",
    radius: float = 6_371_000.0,
    broadcast: bool = False,
) -> xr.DataArray:
    """
    Calculate the area of each grid cell in a rectilinear latitude-longitude grid.
    If longitude spacing is constant a 1D array is returned unless `broadcast` is true.

    Parameters
    ----------
    data : xr.DataArray or xr.Dataset
        Input data containing latitude and longitude dimensions.
    latdim : str, optional
        Name of the latitude dimension in the data. Default is "lat".
    londim : str, optional
        Name of the longitude dimension in the data. Default is "lon".
    radius : float, optional
        Radius of the sphere (e.g., Earth) in meters. Default is 6371000 km.
    broadcast : bool, optional
        If True, broadcast longitude weights to match the shape of the data. Default is False.

    Returns
    -------
    xr.DataArray
        Array of cell areas with the same shape as the input data's spatial dimensions.

    Notes
    -----
    - Assumes latitude and longitude are in degrees.
    - Uses spherical geometry for latitude weighting and linear weighting for longitude.
    """
    lat_weight = area_weights(data, latdim=latdim, kernel=spherical_weights)
    lon_weight = area_weights(data, latdim=londim, kernel=linear_weights) * np.pi / 180  # radians
    if len(np.unique(lon_weight.values)) > 1 or broadcast:
        return radius**2 * lat_weight * lon_weight
    else:
        return radius**2 * lat_weight * lon_weight.values[0]


def area_mean(
    data: xr.DataArray | xr.Dataset,
    region: dict[str, tuple[float, float]] | None = {"lat": (-90, 90), "lon": (-180, 360)},
    weights: xr.DataArray | None = None,
    method: Literal["max", "min", "mean", "std", "sum"] = "mean",
) -> xr.DataArray | xr.Dataset:
    """
    Compute the area weighted mean of the data

    Parameters
    ----------
    data : xr.DataArray | xr.Dataset
        input dataset to be averaged
    region : dict[str, tuple[float, float]] | None, optional
        If set, a region is selected before averaging is performed. By default {"lat": (-90, 90), "lon": (0, 360)}
        Latitude and longitude dimensions are read from the `region` parameter if provided.
    weights : xr.DataArray | None, optional
        User provided weights to used for the average. If not supplied weights are calculated using `area_weights`.

    Returns
    -------
    xr.DataArray | xr.Dataset
        input data after selection and averaging

    Raises
    ------
    ValueError
        If latitude and longitude coordinates cannot be found
    """

    if region is None:
        latdim = "lat"
        londim = "lon"
    else:
        latdim, londim = list(region.keys())

    if not (londim in data.coords and latdim in data.coords):
        raise ValueError("dataset should contain latitude and longitude coordinates")

    if region:
        data = select_region(data, region=region)

    if weights is None:
        weights = cell_area(data, latdim=latdim)

    return getattr(data.weighted(weights), method)(dim=[latdim, londim])


def zonal_mean(data: xr.Dataset | xr.DataArray, lon_dim: str = "lon") -> xr.Dataset | xr.DataArray:
    """Compute the zonal mean

    Parameters
    ----------
    data : xr.Dataset | xr.DataArray
        Data to be averaged.
    lon_dim : str, optional
        name of longitude dimension over which to average, by default "lon".

    Returns
    -------
    xr.Dataset | xr.DataArray
        Zonally averaged data
    """
    return data.mean(dim=lon_dim)


def monthly_mean(data: xr.Dataset | xr.DataArray) -> xr.Dataset | xr.DataArray:
    """resample data to monthly resolution

    Parameters
    ----------
    data : xr.Dataset | xr.DataArray
        input data to be resampled

    Returns
    -------
    xr.Dataset | xr.DataArray
        Monthly averaged data
    """

    return data.resample("time.month").mean(dim="time")


def mask_where(
    data: xr.Dataset | xr.DataArray, mask: xr.Dataset | xr.DataArray, **kwargs
) -> xr.Dataset | xr.DataArray:
    """Work around for the fact that dask does not properly parse kwargs in local mode

    https://github.com/dask/dask/issues/3741
    """

    return data.where(~to_array(mask), **kwargs)


def rename(data: xr.DataArray | xr.Dataset, name: str):
    """rename an array or dataset that has a single array"""
    if isinstance(data, xr.Dataset):
        return to_dataset(to_array(data).rename(name))

    return data.rename(name)


def merge_netcdf(
    paths: list[Path] | list[str],
    output_file: str | Path,
    remove_input_files: bool = True,
    prerequisites: list | None = None,
    open_kwargs: dict | None = {},
    write_kwargs: dict | None = {},
):
    """Save list of temp files to merged netCDF files

    Parameters
    ----------
    paths: (list)
        list of NetCDF filenames
    output_file: (str)
        name of NetCDF file for the list of files to be merged into
    remove_input_files: (bool)
        If true, input files are removed after merging
    prerequisites: (list)
        A possible list of prerequisites that can be used by dask to ensure files are created before calling.

    """
    xr.open_mfdataset(paths, **open_kwargs).to_netcdf(output_file, **write_kwargs)

    if remove_input_files:
        for f in paths:
            Path(f).unlink()

    return
