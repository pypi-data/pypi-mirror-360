from canproc.pipelines.utils import convert_shortform_dag


def test_full_dag():

    dag = {
        "dag": [
            {
                "name": "first",
                "function": "xr.self.isel",
                "args": ["PX"],
                "kwargs": {"level": 0},
            }
        ],
        "output": "first",
    }

    fdag = convert_shortform_dag(dag)
    assert fdag["dag"] == dag["dag"]
    assert fdag["output"] == [dag["output"]]


def test_simple_xr_func():

    fdag = convert_shortform_dag(
        [
            {
                "function": "xr.self.isel",
            }
        ],
        "PX",
    )

    assert len(fdag["dag"]) == 1
    assert fdag["dag"][0]["args"] == ["PX"]
    assert fdag["output"] == [fdag["dag"][0]["name"]]


def test_chained_xr_func():

    fdag = convert_shortform_dag(
        [{"function": "xr.self.isel", "kwargs": {"level": 0}}, {"function": "xr.self.mean"}],
        "PX",
    )

    assert len(fdag["dag"]) == 2
    assert fdag["dag"][0]["args"] == ["PX"]
    assert fdag["dag"][0]["kwargs"] == {"level": 0}
    assert fdag["dag"][1]["args"] == [fdag["dag"][0]["name"]]
    assert fdag["dag"][1]["name"] != fdag["dag"][0]["name"]
    assert fdag["output"] == [fdag["dag"][1]["name"]]


def test_chained_xr_func_w_names():

    fdag = convert_shortform_dag(
        [
            {"function": "xr.self.isel", "name": "first", "kwargs": {"level": 0}},
            {"function": "xr.self.mean", "name": "second", "args": ["first"]},
        ],
        "PX",
    )

    assert len(fdag["dag"]) == 2
    assert fdag["dag"][0]["args"] == ["PX"]
    assert fdag["dag"][0]["kwargs"] == {"level": 0}
    assert fdag["dag"][1]["args"] == [fdag["dag"][0]["name"]]
    assert fdag["dag"][1]["name"] != fdag["dag"][0]["name"]
    assert fdag["output"] == [fdag["dag"][1]["name"]]
