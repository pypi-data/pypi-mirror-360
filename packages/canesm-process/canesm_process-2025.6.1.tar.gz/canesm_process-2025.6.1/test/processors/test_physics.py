from canproc.processors.physics import (
    interpolate_pressure_to_altitude_hypsometric,
    interpolate_to_pressure,
    fast_linear_interp,
)
import pytest
import numpy as np
import xarray as xr


def cmip6_plev():
    return np.array(
        [
            100000.0,
            92500.0,
            85000.0,
            70000.0,
            60000.0,
            50000.0,
            40000.0,
            30000.0,
            25000.0,
            20000.0,
            15000.0,
            10000.0,
            7000.0,
            5000.0,
            3000.0,
            2000.0,
            1000.0,
            700.0,
            500.0,
            300.0,
            200.0,
            100.0,
        ]
    )[::-1]


def generate_plev_data(data):
    plev = cmip6_plev()[::-1]
    lat = [1.395309]
    lon = [180.0]
    time = [np.datetime64("1979-01-16 12:00:00")]
    return xr.DataArray(
        np.expand_dims(data, axis=(0, 2, 3)),
        dims=["time", "plev", "lat", "lon"],
        coords=[time, plev, lat, lon],
    )


def generate_model_level_data(data):
    plev = cmip6_plev()
    level = np.arange(0, len(plev)) / len(plev)
    lat = [-45, 0, 45]
    lon = [-150, -90, -30, 30, 90, 150]
    time = [np.datetime64("1979-01-16 12:00:00"), np.datetime64("1979-02-14 12:00:00")]
    return xr.DataArray(
        data=np.tile(data, [len(time), len(lat), len(lon), 1]),
        dims=["time", "lat", "lon", "level"],
        coords=[time, lat, lon, level],
    )


@pytest.fixture()
def geopotential_height():
    return generate_plev_data(
        np.array(
            [
                51.514843,
                735.8145,
                1466.1454,
                3105.7039,
                4373.565,
                5832.229,
                7558.27,
                9679.323,
                10958.566,
                12448.173,
                14251.253,
                16592.805,
                18591.885,
                20608.094,
                23784.965,
                26412.266,
                31057.271,
                33488.508,
                35824.023,
                39550.445,
                42655.703,
                48064.65,
            ]
        )
    )


@pytest.fixture()
def temperature():
    return generate_plev_data(
        np.array(
            [
                299.4967,
                294.4713,
                291.10654,
                283.17514,
                276.44437,
                268.63263,
                258.95068,
                244.29887,
                234.48796,
                221.64804,
                206.75763,
                189.84383,
                198.36491,
                208.87149,
                217.08853,
                224.71947,
                231.85716,
                233.88535,
                241.1477,
                257.46854,
                263.63553,
                269.30783,
            ]
        )
    )


@pytest.fixture()
def model_level_data():
    length = len(cmip6_plev())
    return generate_model_level_data(np.array([np.random.rand() for l in range(length)]))


def test_altitude_interpolation(geopotential_height, temperature):
    """
    Test the hypsometric interpolation by iterating over zg, ta profiles and interpolating the known value.
    """

    diff_ln_pres = []
    diff = []
    for pidx, pressure in enumerate(temperature.plev.values[1:-1]):

        zg_temp = geopotential_height.where(geopotential_height.plev != pressure, drop=True)
        ta_temp = temperature.where(geopotential_height.plev != pressure, drop=True)

        alt = np.array([float(geopotential_height.sel(plev=pressure).values.squeeze())])
        int_pressure = interpolate_pressure_to_altitude_hypsometric(
            zg_temp, ta_temp, xr.DataArray(alt, dims="altitude", coords=[alt])
        )
        diff.append((int_pressure.values.squeeze() - pressure) / pressure * 100)

        # compute simple log-pressure space interpolation for comparison
        int_ln_pressure = np.exp(
            np.interp(alt, zg_temp.values.squeeze(), np.log(zg_temp.plev.values))
        )
        diff_ln_pres.append((int_ln_pressure - pressure) / pressure * 100)

    # Allow max error of 1%. Typically should be better but this can occur when the
    # tropopause is not sampled and it is difficult to estimate temperature
    assert np.all(np.abs(np.array(diff)) < 1.0)

    # On average hypsometric equation should provide improvement over log-pressure interpolation
    assert np.sum(np.array(diff) ** 2) < np.sum(np.array(diff_ln_pres) ** 2)


def test_model_level_to_pressure_interpolation(model_level_data):

    pressure = generate_model_level_data(cmip6_plev())
    nlevels = len(cmip6_plev())
    levels = np.arange(0, nlevels) / nlevels
    out_pressure = xr.DataArray(cmip6_plev() * 0.99, coords=[levels], dims=["plev"])
    data = interpolate_to_pressure(
        model_level_data, input_pressure=pressure, output_pressure=out_pressure
    )

    # do a simple linear interpolation in log space as a check
    linterp = np.interp(
        np.log(out_pressure.values),
        np.log(pressure.isel(lat=0, lon=0, time=0).values),
        model_level_data.isel(lat=0, lon=0, time=0).values,
    )

    # np.interp doesn't extrapolate, so the last value is expected to be different
    np.testing.assert_allclose(data.isel(lat=0, lon=0, time=0).values[:-1], linterp[:-1])
    # assert np.all(data.isel(lat=0, lon=0, time=0).values[:-1] - linterp[:-1] == 0.0)


if __name__ == "__main__":

    from time import time
    from pathlib import Path

    folder = Path(
        "/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/data/jcl-diag-test-a-009/aya_regrid/regrid_365/ncdir/2004010100_00"
    )
    pressure_file = folder / "PX.nc"
    uu_file = folder / "UU.nc"

    pressure = xr.open_mfdataset(pressure_file)
    uu = xr.open_mfdataset(uu_file)
    # out_pressure = np.array([100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 200, 100, 20], dtype=np.float32) / 100
    out_pressure = np.logspace(1, 5, 50, dtype=np.float32) / 100
    N = 100

    start = time()

    uus = uu.isel(time=slice(0, N)).chunk(time=N, lat=-1, lon=-1, level=-1).load()
    pressures = (
        pressure.isel(time=slice(0, N))
        .isel(level=np.arange(0, 98, 2))
        .chunk(time=N, lat=-1, lon=-1, level=-1)
        .load()
    )
    end = time()
    print(f"data loading took {(end - start) / N:0.2f} seconds per slice")
    start = time()

    uu_on_pressure = interpolate_to_pressure(uus.UU, pressures.PX, out_pressure)
    uu_on_pressure.values
    end = time()
    print(f"pressure interpolation took {(end - start) / N:0.4f} seconds per slice")
