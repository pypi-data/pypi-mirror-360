from canproc.pipelines import Pipeline

from canproc.runners import DaskRunner, DaskDistributedRunner
from pathlib import Path
import pytest
import os


@pytest.mark.skip(reason="requires access to science")
def test_run_pipeline(runner, plot_dag: bool = False):

    import time
    from dask.diagnostics import Profiler, ResourceProfiler, CacheProfiler, visualize
    from dask.distributed import performance_report

    # qsub -I -lselect=1:ncpus=1:mem=10gb -lplace=scatter -Wumask=022 -S/bin/bash -qdevelopment -lwalltime=02:00:00
    # config = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/templates/canproc_tests/metadata/tables/core_cmip6.yaml"
    # config = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rlr001/software/pipelines/canesm-processor/test/tables/core_cmip6.yaml"
    # config = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rlr001/software/canesm-processor/config/cmip/dev_cmip6.yaml"
    # config = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rlg001/repos/canesm-processor/rtd_reuse_test.yaml"
    # config = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/store/canesm-processor/test/cmip6/run_cmip6.py"
    # config = "/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/store/canesm-processor/test/cmip6/config/core_cmip6.yaml"
    config = Path(__file__).parent.parent / "data" / "pipelines" / "test_pressure_interp.yaml"
    # config = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rlr001/software/canesm-processor/test/data/pipelines/test_multistage_branching.yaml"
    # config = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rlr001/software/pipelines/canesm-processor/test/tables/"
    input_dir = "/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/data/jcl-diag-test-a-009/aya_regrid/regrid_365/ncdir/2004010100_00"
    # input_dir = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/data/jcl-diag-test-a-009/1.0x1.0_monthly/ncdir"
    # input_dir = "/fs/site6/eccc/crd/ccrn/users/aya001/canesm_runs/v6b1-lakendg-aya/data"
    # output_dir = r"/space/hall5/sitestore/eccc/crd/ccrn/users/rlr001/canproc/jcl-diag-test-a-009-cmip"
    output_dir = "/space/hall5/sitestore/eccc/crd/ccrn/users/rlr001/canproc/pressure_interp"

    # config = "/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/store/canesm-processor/test/cmip6/config/core_cmip6.yaml"
    # output = cwd + "/output/cmip6/"
    # input_dir = "/space/hall5/sitestore/eccc/crd/ccrn/users/rvs001/data/jcl-diag-test-a-009/aya_regrid/regrid_365/ncdir/2004010100_00"

    print("creating pipeline...")
    pipeline = Pipeline(config, input_dir, output_dir)
    dag = pipeline.render()

    dsk, output = runner.create_dag(dag)

    if plot_dag:
        from dask.dot import dot_graph

        dot_graph(
            dsk, f"{Path(config).name.split('.')[0]}.png", rankdir="TB", collapse_outputs=True
        )

    print("creating output directories...")
    for directory in pipeline.directories.values():
        os.makedirs(directory, exist_ok=True)

    start = time.time()
    print("running dag...")
    runner.run(dag, optimize=False)
    end = time.time()
    print(f"processing took {end - start:3.4f} seconds")
    print("SUCCESS!")


if __name__ == "__main__":

    runner = DaskDistributedRunner(workers=10, threads_per_worker=1)
    test_run_pipeline(runner, plot_dag=False)
