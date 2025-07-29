from canproc.processors.base import (
    area_mean,
    area_weights,
    mask_where,
    select_region,
    zonal_mean,
    add_metadata,
    cell_area,
)
import xarray as xr
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def dataset():

    lons = np.arange(-150, 151, 30.0)
    lats = np.arange(-60, 61, 30.0)
    time = pd.date_range("2014-09-06", periods=4)
    temperature = np.ones((len(lats), len(lons), len(time)))
    return xr.Dataset(
        {
            "temperature": (["lat", "lon", "time"], temperature),
        },
        coords={
            "lat": lats,
            "lon": lons,
            "time": time,
        },
    )


@pytest.fixture
def mask():

    lons = np.arange(-150, 151, 30.0)
    lats = np.arange(-60, 61, 30.0)
    time = pd.date_range("2014-09-06", periods=4)
    mask_array = np.ones((len(lats), len(lons), len(time)), dtype=bool)
    return xr.Dataset(
        {
            "mask": (["lat", "lon", "time"], mask_array),
        },
        coords={
            "lat": lats,
            "lon": lons,
            "time": time,
        },
    )


@pytest.fixture
def dataset_with_bounds(dataset):
    lat = dataset.lat.to_numpy()
    lat_bnds = np.arange(-75, 76, 30.0)
    dataset["lat_bnds"] = xr.DataArray(
        np.array([(a, b) for a, b in zip(lat_bnds[0:-1], lat_bnds[1:])]),
        dims=["lat", "bnds"],
        coords=[lat, [0, 1]],
    )
    return dataset


def test_area_weights(dataset):
    weights = area_weights(dataset)
    assert weights.to_numpy() == pytest.approx(
        [0.25881905, 0.44828774, 0.51763809, 0.44828774, 0.25881905]
    )


def test_area_weights_with_bounds(dataset_with_bounds):
    weights = area_weights(dataset_with_bounds)
    assert weights.to_numpy() == pytest.approx(
        [0.25881905, 0.44828774, 0.51763809, 0.44828774, 0.25881905]
    )


def test_area_mean(dataset):
    ds = area_mean(dataset)
    assert ds.temperature.shape == (4,)
    assert ds.temperature.mean() == 1.0


def test_area_mean_with_region(dataset):
    ds = area_mean(dataset, region={"lat": (0, 90), "lon": (0, 180)})
    assert ds.temperature.shape == (4,)
    assert ds.temperature.mean() == 1.0


def test_area_sum(dataset):
    ds = area_mean(dataset, method="sum")

    total_area = (
        np.deg2rad(330.0) * (np.sin(np.deg2rad(75)) - np.sin(np.deg2rad(-75))) * 6371000.0**2
    )
    assert float(ds.temperature.isel(time=0).values) == pytest.approx(float(total_area))


def test_zonal_mean(dataset):
    ds = zonal_mean(dataset)
    assert ds.temperature.shape == (5, 4)
    assert ds.temperature.mean() == 1.0


def test_mask_where(dataset, mask):
    # check that masking using a dataset (as opposed to an array) works
    ds1 = mask_where(dataset, mask)
    assert np.isnan(ds1.temperature.mean())
    ds1 = mask_where(dataset, mask == 0)
    assert ds1.temperature.mean() == 1.0


def test_select_region(dataset):
    ds = select_region(dataset, {"lat": (0, 90), "lon": (0, 180)})
    assert ds.temperature.shape == (3, 6, 4)


def test_select_region_dateline(dataset):
    ds = select_region(dataset, {"lat": (0, 90), "lon": (150, -30)})
    assert ds.lon.to_numpy() == pytest.approx([-150, -120, -90, -60, -30, 150])

    ds = select_region(dataset, {"lat": (0, 90), "lon": (-30, 150)})
    assert ds.lon.to_numpy() == pytest.approx([-30, 0, 30, 60, 90, 120, 150])

    ds = select_region(dataset, {"lat": (0, 90), "lon": (-150, 30)})
    assert ds.lon.to_numpy() == pytest.approx([-150, -120, -90, -60, -30, 0, 30])


def test_select_region_0_360(dataset):
    dataset.coords["lon"] = dataset.coords["lon"] % 360
    dataset = dataset.sortby(dataset.lon)

    ds = select_region(dataset, {"lat": (0, 90), "lon": (-150, 30)})
    assert ds.lon.to_numpy() == pytest.approx([0, 30, 210, 240, 270, 300, 330])

    ds = select_region(dataset, {"lat": (0, 90), "lon": (50, 90)})
    assert ds.lon.to_numpy() == pytest.approx([60, 90])

    ds = select_region(dataset, {"lat": (0, 90), "lon": (300, 90)})
    assert ds.lon.to_numpy() == pytest.approx([0, 30, 60, 90, 300, 330])

    ds = select_region(dataset, {"lat": (0, 90), "lon": (150, -30)})
    assert ds.lon.to_numpy() == pytest.approx([150, 210, 240, 270, 300, 330])


def test_add_metadata(dataset):

    ds = add_metadata(dataset, {"long_name": "Temperature at surface"})
    assert ds["temperature"].attrs == {"long_name": "Temperature at surface"}


def test_add_metadata_with_min(dataset):
    ds = add_metadata(dataset, {"long_name": "Temperature at surface", "min": True})
    assert ds["temperature"].attrs == {"long_name": "Temperature at surface", "min": 1.0}


def test_add_metadata_with_minmax(dataset):

    ds = add_metadata(dataset, {"long_name": "Temperature at surface", "min": True, "max": True})
    assert ds["temperature"].attrs == {
        "long_name": "Temperature at surface",
        "min": 1.0,
        "max": 1.0,
    }


def test_cell_area(dataset):

    # dataset from 75N to 75S, 15E to 345E
    true_area = float(
        np.deg2rad(330.0) * (np.sin(np.deg2rad(75)) - np.sin(np.deg2rad(-75))) * 6371.0**2
    )

    ds = cell_area(dataset, radius=6371.0)
    weighted_area = float((dataset.temperature.isel(time=0) * ds).sum().values)
    assert weighted_area == pytest.approx(true_area)

    ds = cell_area(dataset, radius=6371.0, broadcast=True)
    weighted_area = float(ds.sum().values)
    assert weighted_area == pytest.approx(true_area)
