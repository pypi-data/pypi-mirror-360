from canproc.runners import DaskRunner
from canproc import DAG
from dask.distributed import LocalCluster


class DaskDistributedRunner(DaskRunner):
    """
    Use dask distributed to run a directed acyclic graph. Memory is distributed equally over the workers
    so is recommended to reduce workers if memory issues arise.

    Attributes
    ----------
    scheduler : Callable
    client : Dask client
    cluster : Dask cluster

    Examples
    --------
    >>> from canproc.runners import DaskDistributedRunner
    >>> from canproc import DAG, DAGProcess
    >>> dag = DAG(dag=[DAGProcess(name='array', function='np.arange', args=[0, 10])], output='array')
    >>> runner = DaskDistributedRunner()
    >>> array = runner.run(dag)
    """

    def __init__(
        self,
        processes=True,
        workers=1,
        threads_per_worker=1,
        **kwargs,
    ):
        """

        Parameters
        ----------
        workers : int, optional
            Number of dask workers to use. Defaults to 1
        threads_per_worker: int, optional
            Number of threads each worker will spawn. Defaults to 1
        processes: bool, optional
            Whether to use processes or threads. Defaults to True (processes)
        """
        workers = kwargs.pop("workers", workers)
        threads_per_worker = kwargs.pop("threads_per_worker", threads_per_worker)
        processes = kwargs.pop("processes", processes)

        self.cluster = LocalCluster(
            processes=processes, n_workers=workers, threads_per_worker=threads_per_worker, **kwargs
        )

        self.client = self.cluster.get_client()
        self.scheduler = self.client.get
