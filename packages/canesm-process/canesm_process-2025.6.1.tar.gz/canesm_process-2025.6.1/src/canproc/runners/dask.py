from canproc.dag.dag import DAG
from dask.utils import apply
import dask
from typing import Any, Callable, Literal
from dask.optimization import cull, inline, inline_functions, fuse


DaskTaskType = tuple[Callable, Callable, list, dict]
DaskOutputType = str | list[str]
DaskDagType = dict[str, DaskTaskType]


class DaskRunner:
    """
    Use dask to run a directed acyclic graph

    Attributes
    ----------
    scheduler : Callable

    Examples
    --------
    >>> from canproc.runners import DaskRunner
    >>> from canproc import DAG, DAGProcess
    >>> dag = DAG(dag=[DAGProcess(name='array', function='np.arange', args=[0, 10])], output='array')
    >>> runner = DaskRunner()
    >>> array = runner.run(dag)
    """

    def __init__(
        self,
        scheduler: Literal["threads", "processes", "single-threaded", "syncronous"] = "threads",
    ):
        """

        Parameters
        ----------
        scheduler : str, optional
            Accepts "threads", "processes" or "single-threaded" by default "threads"

        """
        match scheduler:
            case "threads":
                self.scheduler = dask.threaded.get
            case "processes":
                self.scheduler = dask.multiprocessing.get
            case "syncronous":
                self.scheduler = dask.get
            case "single-threaded":
                self.scheduler = dask.get
            case _:
                raise ValueError(f"scheduler {scheduler} is not recognized")

    @staticmethod
    def create_dag(dag: DAG, optimize: bool = False) -> tuple[DaskDagType, DaskOutputType]:
        """
        Format the DAG into the format dask expects
        """
        dsk = {}
        for process in dag.dag:
            dsk[process.name] = (
                apply,
                process.function,
                process.args,
                process.kwargs if process.kwargs else {},
            )

        if optimize:
            dsk = DaskRunner.optimize_graph(dsk, dag.output)

        return dsk, dag.output

    @staticmethod
    def optimize_graph(dsk: dict, outputs: list[str]):
        dsk1, deps = cull(dsk, outputs)
        dsk2 = inline(dsk1, dependencies=deps)
        # dsk3 = inline_functions(dsk2, keys, [len, str.split],
        # dependencies=deps)
        dsk4, deps = fuse(dsk2)
        return dsk4

    def run(self, dag: DAG, optimize=False, **kwargs) -> Any:
        """Run a DAG using the dask scheduler

        Parameters
        ----------
        dag : DAG
            Directed Acyclic Graph that defines the processes and outputs

        Returns
        -------
        output
            Output of the dag

        """
        dsk, output = self.create_dag(dag, optimize=optimize)
        return self.scheduler(dsk, output, **kwargs)
