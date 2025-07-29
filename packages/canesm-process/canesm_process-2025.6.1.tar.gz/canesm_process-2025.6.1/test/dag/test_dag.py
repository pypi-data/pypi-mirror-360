from canproc.dag.dag import merge
from canproc.dag.dag import DAG, DAGProcess
from canproc.runners import DaskRunner, DaskDistributedRunner
from canproc.processors.base import area_mean
import numpy as np
import json
import pytest


@pytest.fixture()
def model_str():
    return """{
        "dag": [
            {"name": "load1", "function": "np.arange", "args": [8]},
            {"name": "load2", "function": "np.arange", "args": [0, 4]},
            {
                "name": "concat",
                "function": "np.concatenate",
                "args": [["load1", "load2"]]
            },
            {"name": "mean", "function": "np.mean", "args": ["concat"]}
        ],
        "output": "mean"
    }"""


@pytest.fixture
def model_dict(model_str):
    return json.loads(model_str)


def test_np_function_factory():
    proc = DAGProcess(name="testnp", function="np.arange", args=[8])
    assert proc.function is np.arange


def test_processor_function_factory():
    proc = DAGProcess(name="areamean", function="area_mean")
    assert proc.function == area_mean


def test_numpy_serialization():
    # simple numpy function
    proc = DAGProcess(name="testnp", function="np.arange", args=[8])
    assert proc.model_dump() == {
        "name": "testnp",
        "function": "numpy.arange",
        "args": [8],
        "kwargs": None,
    }

    # concatenate is a wrapped builtin
    proc = DAGProcess(name="testnp", function="np.concatenate", args=[[[0], [1]]])
    assert proc.model_dump() == {
        "name": "testnp",
        "function": "numpy.concatenate",
        "args": [[[0], [1]]],
        "kwargs": None,
    }


@pytest.mark.parametrize("scheduler", ["threads", "processes", "single-threaded"])
def test_dag(scheduler):

    dag = DAG(
        dag=[
            DAGProcess(name="load1", function=np.arange, args=[8]),
            DAGProcess(name="load2", function=np.arange, args=[0, 4]),
            DAGProcess(name="concat", function="np.concatenate", args=[["load1", "load2"]]),
            DAGProcess(name="mean", function=np.mean, args=["concat"]),
        ],
        output="mean",
    )
    runner = DaskRunner(scheduler=scheduler)
    x = runner.run(dag)
    assert x == pytest.approx(2.833333333, abs=1e-6)


# @pytest.mark.parametrize("Runner", [DaskRunner, RayRunner])
def test_from_json(model_dict):

    dag = DAG.model_validate(model_dict)
    runner = DaskRunner()
    x = runner.run(dag)
    assert x == pytest.approx(2.833333333, abs=1e-6)


# def test_ray_runner(model_dict):

#     dag = DAG.model_validate(model_dict)
#     runner = RayRunner()
#     x = runner.run(dag, ray_init_kwargs={'num_cpus': 1, 'include_dashboard': False})
#     assert x == pytest.approx(2.833333333, abs=1e-6)


def test_from_str(model_str):

    dag = DAG(**json.loads(model_str))
    runner = DaskRunner()
    x = runner.run(dag)
    assert x == pytest.approx(2.833333333, abs=1e-6)


def test_dag_process_id():

    # check the same process creates the same id
    p1 = DAGProcess(name="load1", function=np.arange, args=[8])
    p1_dup = DAGProcess(name="load1", function=np.arange, args=[8])
    assert p1.id == p1_dup.id

    # check that a name change alters the id
    p2 = DAGProcess(name="load2", function=np.arange, args=[8])
    assert p1.id != p2.id

    # check that a change in args changes the id
    p3 = DAGProcess(name="load1", function=np.arange, args=[0, 8])
    assert p3.id != p1.id

    # check that a function and function name produce the same id
    p3_dup = DAGProcess(name="load1", function="np.arange", args=[0, 8])
    assert p3.id == p3_dup.id


def test_dag_id(model_dict):
    dag = DAG.model_validate(model_dict)
    assert dag.id[0:8] == "117595e5"


def test_dag_merge(model_dict):
    dag1 = DAG.model_validate(model_dict)
    dag2 = DAG(
        dag=[DAGProcess(name="arange", function=lambda x: np.arange(int(x)), args=["mean"])],
        output="arange",
    )

    fulldag = merge([dag1, dag2])
    assert len(fulldag.dag) == 5
    assert fulldag.output == "arange"


def test_dag_merge_keep(model_dict):
    dag1 = DAG.model_validate(model_dict)
    dag2 = DAG(
        dag=[DAGProcess(name="arange", function=lambda x: np.arange(int(x)), args=["mean"])],
        output="arange",
    )

    fulldag = merge([dag1, dag2], keep_intermediate=True)
    assert len(fulldag.dag) == 5
    assert fulldag.output == ["mean", "arange"]


def test_dask_distributed_client(model_dict):

    runner = DaskDistributedRunner(workers=1, threads_per_worker=1)
    x = runner.run(DAG(**model_dict))
    assert x == pytest.approx(2.833333333, abs=1e-6)
