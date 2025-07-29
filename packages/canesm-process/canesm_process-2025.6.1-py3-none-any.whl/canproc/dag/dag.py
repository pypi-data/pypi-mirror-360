from typing import Callable
from pydantic import BaseModel, field_serializer, field_validator
from hashlib import sha256
from canproc.dag.utils import function_factory, serialize_function


class DAGProcess(BaseModel):
    """A single processing node in a DAG

    Attributes
    ----------
    name : str
        name of the node. Used to connect multiple nodes in a DAG.
    function : Callable | str
        A function used to process the node. If a string then this is converted to a function.
    args : list
        List of input arguments to the function.
    kwargs : dict
        Dictionary of key word arguments to the function.

    Examples
    --------
    >>> proc = DAGProcess(name='make_array', function=np.arange, args=[8])

    """

    name: str
    function: Callable | str
    args: list | None = None
    kwargs: dict | None = None

    @property
    def id(self):
        return sha256(self.model_dump_json().encode("utf-8")).hexdigest()

    @field_validator("function")
    @classmethod
    def convert_str_to_function(cls, function: str | Callable) -> Callable:
        if isinstance(function, str):
            return function_factory(function)
        else:
            return function

    @field_serializer("function")
    def function_serializer(self, func: Callable):
        return serialize_function(func)

    def __repr__(self):
        try:
            name = self.function.__name__
        except:
            name = "functools.partial"
        return f"{self.name} = {name}({self.args}, {self.kwargs})"


class DAG(BaseModel):
    """
    A directed acyclic graph defines the program flow. Each node in the graph
    is a process to be ran, and each edge (the node connections) are the input
    and outputs of the process. Importantly, a DAG need not be a simple linear
    pipeline, but may include parallel branching and execution so long as it
    does not include a cycle (as this would cause infinite recursion).

    Attributes
    ----------
    dag : list[DAGProcess]
        list of `DAGProcess` that make up the directed acyclic graph
    output : str | list[str]
        Name(s) of the graph edges to return

    #TODO: Add validator to check for cyclic graphs
    """

    dag: list[DAGProcess]
    output: str | list[str]

    @property
    def id(self):
        # order of dag elements does not matter
        ids = sorted([el.id for el in self.dag])
        ids += sorted(self.output)
        return sha256("".join(ids).encode("utf-8")).hexdigest()

    def get_nodes_by_name(self, name: str, exclude: str | None = None) -> list[DAGProcess]:
        nodes = []
        for node in self.dag:
            if name in node.name and (exclude is None or exclude not in node.name):
                nodes.append(node)
        return nodes

    def __repr__(self):
        out = "DAGProcesses:\n"
        out += "\n".join([f"   * {d!r}" for d in self.dag])
        out += "\nOutput:\n"
        if type(self.output) is str:
            out += f"   * {self.output}"
        else:
            out += "\n".join([f"   * {d}" for d in self.output])
        return out


def merge(dags: list[DAG], keep_intermediate: bool = False) -> DAG:
    """
    Merge multiple DAGs into a single graph

    Parameters
    ----------
    dags : list[DAG]
        the DAGs to be merged
    keep_intermediate : bool, optional
        if `True` the output of all DAGs is returned. If `False`, only the
        output of the final DAG is kept. By default `False`

    Returns
    -------
    DAG
        Merged DAG
    """

    if len(dags) == 1:
        return dags[0]

    fulldag = dags[0].dag
    if keep_intermediate:
        output = []
        if type(dags[0].output) is list:
            output.extend(dags[0].output)
        else:
            output.append(dags[0].output)

    for dag in dags[1:]:
        fulldag.extend(dag.dag)
        if keep_intermediate:
            if type(dag.output) is list:
                output.extend(dag.output)
            else:
                output.append(dag.output)

    if not keep_intermediate:
        output = dags[-1].output

    return DAG(dag=fulldag, output=output)
