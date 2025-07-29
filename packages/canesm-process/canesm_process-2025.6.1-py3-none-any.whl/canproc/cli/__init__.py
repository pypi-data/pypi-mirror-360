import click
import json
from canproc import DAG, merge
from canproc.runners import DaskRunner, DaskDistributedRunner
from canproc.pipelines.pipelines import Pipeline
import os
from pathlib import Path
import logging


@click.command()
@click.argument("dags", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--scheduler",
    default="threads",
    help="The dask scheduler to be used, threads, processes or single-threaded",
)
def run(dags, scheduler):
    """Combine and run a series of DAGs.

    Example
    -------

    >>> canproc-run "load_region_data.json" "monthly_anomalies.json" "enso.json" "to_netcdf.json"

    """

    dag_list = []
    for filename in dags:
        dag_list.append(DAG(**json.load(open(filename, "r"))))

    dag = merge(dag_list)

    runner = DaskRunner(scheduler=scheduler)
    runner.run(dag)


@click.command()
@click.argument("config", nargs=1, type=click.Path(exists=True))
@click.argument("input", nargs=1, type=click.Path(exists=True))
@click.argument("output", nargs=1, type=click.Path(), default=None, required=False)
@click.option(
    "-s",
    "--scheduler",
    default="threads",
    type=click.Choice(["threads", "processes", "distributed", "single-threaded", "syncronous"]),
    help="The dask scheduler to be used, threads, processes, distributed or single-threaded",
)
@click.option(
    "-w",
    "--workers",
    default=80,
    type=int,
    help="number of workers that will be used for distributed runner.",
)
@click.option(
    "-t",
    "--threads_per_worker",
    default=1,
    type=int,
    help="number of threads per worker when using distributed runner",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="print the created dag but do not run, useful for debugging",
)
def process_pipeline(config, input, output, scheduler, workers, threads_per_worker, dry_run):
    """Run a data pipeline

    \b
    CONFIG: Path to the config file
    INPUT: Directory containing the input files
    OUTPUT: Directory where output files will be written

    \b
    Example
    -------

    >>> canproc-pipeline "config.yaml" "/space/hall5/sitestore/..."

    """

    pipeline = Pipeline(config, input, output)
    dag = pipeline.render()

    if dry_run:  # useful for testing
        click.echo(dag)
        return

    if output is None:
        output = input
    else:
        output = Path(output)

    for directory in pipeline.directories.values():
        os.makedirs(directory, exist_ok=True)

    if scheduler == "distributed":
        runner = DaskDistributedRunner(workers=workers, threads_per_worker=threads_per_worker)
    else:
        runner = DaskRunner(scheduler=scheduler)

    runner.run(dag)
