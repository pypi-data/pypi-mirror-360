import pytest
import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
from canproc.runners import DaskRunner
from canproc.pipelines import Pipeline
from canproc.runners import DaskRunner


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


def test_end_to_end(tmp_path, dataset):

    input = tmp_path / "end_to_end" / "input"
    output = tmp_path / "end_to_end" / "output"
    config = Path(__file__).parent.parent / "data" / "pipelines" / "test_end_to_end.yaml"

    input.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)

    dataset.to_netcdf(input / "temperature.nc")

    pipeline = Pipeline(config=config, input_dir=input, output_dir=output)

    for directory in pipeline.directories.values():
        directory.mkdir(parents=True, exist_ok=True)

    dag = pipeline.render()

    runner = DaskRunner()
    runner.run(dag)

    # files = list((output / "diags" / "test").glob("*"))
    # assert len(files) == 1
    # assert files[0].name == "TS.nc"

    files = list((output / "diags" / "test").glob("*"))
    assert len(files) == 1
    assert files[0].name == "temperatures.nc"
