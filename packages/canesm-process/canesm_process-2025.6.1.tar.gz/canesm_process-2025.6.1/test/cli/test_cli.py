from click.testing import CliRunner
from canproc.cli import run, process_pipeline
from pathlib import Path
import pytest


@pytest.fixture()
def pipeline_file():
    file = (
        Path(__file__).parent.parent.parent
        / "src"
        / "canproc"
        / "templates"
        / "pipelines"
        / "canesm_pipeline.yaml"
    )
    return file.absolute().as_posix()


def test_run():
    runner = CliRunner()
    result = runner.invoke(
        run, [(Path(__file__).resolve().parent.parent / "data" / "test.json").as_posix()]
    )
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(2.833333333, abs=1e-6)


def test_run_pipeline(pipeline_file):
    runner = CliRunner()
    result = runner.invoke(
        process_pipeline,
        [
            pipeline_file,
            "test",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
