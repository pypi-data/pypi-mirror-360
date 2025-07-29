from canproc.dag.utils import function_factory
from canproc.dag.dag import DAG, DAGProcess
from canproc.runners import DaskRunner
import xarray as xr
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def dataset():

    temperature = np.ones((2, 3, 4))
    time = pd.date_range("2014-09-06", periods=4)
    return xr.Dataset(
        {
            "temperature": (["lat", "lon", "time"], temperature),
        },
        coords={
            "lat": np.array([0, 1]),
            "lon": np.array([0, 10, 20]),
            "time": time,
        },
    )


@pytest.fixture
def mask():

    lons = np.arange(-150, 151, 30.0)
    lats = np.arange(-60, 61, 30.0)
    time = pd.date_range("2014-09-06", periods=4)
    mask_array = np.zeros((len(lats), len(lons), len(time)))
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


def test_xr_function_factory():
    proc = DAGProcess(name="testxr", function="xr.concat", args=[1, 2])
    assert proc.function is xr.concat


@pytest.mark.parametrize(
    "op, result",
    [
        ("xr.add", 48),
        ("xr.mul", 24),
        ("xr.sub", 0),
        ("xr.truediv", 24),
        ("xr.lt", 0),
        ("xr.le", 24),
        ("xr.pow", 24),
        ("xr.eq", 24),
    ],
    ids=[
        "add",
        "multiipy",
        "subtract",
        "divide",
        "less than",
        "less than equal",
        "power",
        "equality",
    ],
)
def test_xarray_operator(dataset, op, result):

    oper = function_factory(op)
    ds = oper(dataset, dataset)
    ds["temperature"].sum() == result

    oper = function_factory(op)
    ds = oper(dataset, 1)
    ds["temperature"].sum() == result

    oper = function_factory(op)
    ds = oper(1, dataset)
    ds["temperature"].sum() == result


def test_self_operator(dataset):
    op = function_factory("xr.self.mean")
    ds = op(dataset, **{"dim": "time"})

    assert ds.temperature.shape == (2, 3)
    assert ds.temperature.sum() == 2 * 3


def test_dag_process(dataset):

    proc = DAGProcess(name="add", function="xr.add", args=[dataset, dataset])
    mean = DAGProcess(name="mean", function="xr.self.mean", args=["add"], kwargs={"dim": "time"})

    runner = DaskRunner()
    out = runner.run(dag=DAG(dag=[proc, mean], output="mean"))
    assert out.temperature.shape == (2, 3)
    assert out.temperature.sum() == 2 * 3 * 2

    proc = DAGProcess(name="add", function="xr.add", args=[dataset, 7])
    proc2 = DAGProcess(name="add2", function="xr.add", args=["add", 7])
    mean = DAGProcess(name="mean", function="xr.self.mean", args=["add2"], kwargs={"dim": "time"})

    runner = DaskRunner()
    out = runner.run(dag=DAG(dag=[proc, proc2, mean], output="mean"))
    assert out.temperature.sum() == 2 * 3 * (1 + 7 + 7)


@pytest.mark.parametrize(
    "model",
    [
        dict(name="add", function="xarray.add", args=["data1", "data2"], kwargs=None),
        dict(name="mean", function="xarray.self.mean", args=["add"], kwargs={"dim": "time"}),
        dict(name="concat", function="xarray.concat", args=["add"], kwargs={"dim": "time"}),
    ],
    ids=["xr.add", "xr.self.mean", "xr.concat"],
)
def test_xarray_serialization(model):
    assert DAGProcess.model_validate(model).model_dump() == model


def test_array_renaming(dataset):
    # check that operations on dataset with different variable names
    # returns the first dataset name.
    dataset2 = dataset.rename({"temperature": "pressure"})
    oper = function_factory("xr.add")
    ds = oper(dataset, dataset2)
    assert ds.temperature.name == "temperature"
    ds = oper(dataset2, dataset)
    assert ds.pressure.name == "pressure"
