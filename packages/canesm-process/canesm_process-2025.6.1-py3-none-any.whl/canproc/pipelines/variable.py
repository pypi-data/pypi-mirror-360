from canproc.dag import DAGProcess, DAG
from canproc.pipelines.loaders import FileLoader, FileWriter
from canproc.pipelines.utils import UUID, AstParser
from pathlib import Path
from typing import Literal, Any
from typing_extensions import Self
import ast


class TrackedAttribute:

    def __init__(self, tag: str | None = None, value=None):

        self._current = None
        self._value: dict[str, Any] = {}
        if tag and value:
            self._value[tag] = value

    def update(self, tag: str, value):
        self._current = tag
        self._value[tag] = value

    def tag_current(self, tag: str):
        if self._current is None:
            self._value[tag] = self()
        self._value[tag] = self(self._current)

    def __call__(self, tag: str | None = None):

        if tag is not None:
            if tag == "latest":
                try:
                    tag = list(self._value.keys())[0]
                except:
                    return None
            return self._value[tag]

        if self._value.keys():
            return self._value[list(self._value.keys())[-1]]

        return None


class Variable:
    """
    Class to keep track of operations that have been applied to dataset.

    Example
    -------

    >>> variable = Variable('temperature')
    >>> variable.open('test/input_directory', engine='netcdf4')
    >>> variable.scale(10.0)
    >>> variable.write('test/output_directory')
    >>> dag = variable.render()
    """

    # list of operations that can be applied to a variable
    # this is a subset of Variable methods
    allowed_operations = [
        "shift",
        "scale",
        "divide",
        "rename",
        "destination",
        "mask",
        "persist",
        "resample",
        "cycle",
        "area_mean",
        "cell_area",
    ]

    def __init__(
        self,
        name: str,
        loader: FileLoader | None = None,
        writer: FileWriter | None = None,
        metadata: dict = {},
        **kwargs,
    ):
        """Initialization

        Parameters
        ----------
        name : str
            name given to the variable. Used for generating function names
        loader : FileLoader, optional
            custom loader used to load variable
        metadata : dict, optional
            dictionary of metadata assigned to variable
        """

        self.name: str = name  # used for node names
        self.time_dim: str = "time"  # time variable, used in cycles
        self.current_uuid: UUID = UUID()
        self._nodes: list[str] = []
        self.output: list[str] = []
        self.tags: dict[str, str] = {}
        self.operations: list[DAGProcess] = []
        self.metadata = metadata
        self.current_label = None
        self.loader = loader
        self.writer = writer

        # Tracked variables - we need to keep track of these so that a DAG node
        # can refer to a specific version. eg., if a variable is branched and both
        # versions are written to a file they will have different output_filenames.
        # See test pipeline `test_multistage_branching`.
        self.var_name = TrackedAttribute(self.current(), name)
        self.output_filename = TrackedAttribute(self.current(), f"{name}.nc")
        try:
            chunks = loader.kwargs["chunks"]
        except Exception as err:
            if "chunks" in kwargs:
                chunks = kwargs["chunks"]
            else:
                chunks = {}
        self.chunks = TrackedAttribute(self.current(), chunks)
        self.tracked = [self.output_filename, self.chunks, self.var_name]

    @property
    def from_file(self):
        return self.loader is not None

    def destination(self, value: str, reuse_from_tag: str | list[str] | None = None):
        if reuse_from_tag is not None:
            tag = self.get_tag(reuse_from_tag)
        else:
            tag = self.current()
        self.output_filename.update(tag, value)
        try:
            chunks = self.chunks(self.current())
        except KeyError:
            chunks = {}
        self.chunks.update(tag, chunks)

    def next(self, label: str | None = None) -> str:
        """get the next node ID

        Parameters
        ----------
        label : str | None, optional
            include an optional label in the ID, by default None

        Returns
        -------
        str
            ID of the next node
        """
        self.current_uuid = UUID()
        self.current_label = label
        self._nodes.append(self.current())

        return self.current()

    def current(self, custom_label: str | None = None) -> str:
        """current node ID

        Returns
        -------
        str
            current ID
        """
        tmp = f"{self.name}"

        if self.current_label:
            tmp += f"_{self.current_label}"

        if custom_label is not None:
            tmp += f"_{custom_label}"

        tmp += f"-{self.current_uuid.short}"
        return tmp

    def add_tag(self, tag: str):
        """Add a tag that can be used to reference the current node.

        Parameters
        ----------
        tag : str
        """
        self.tags[tag] = self.current()
        self.output_filename.tag_current(self.current())
        self.chunks.tag_current(self.current())
        self.var_name.tag_current(self.current())

    def get_tag(self, tag: str | list[str], allow_fallback: bool = False) -> str:
        """get the ID of the node with the tag. If a list is provided then return the first valid.

        Parameters
        ----------
        tag : str | list[str]
        allow_fallback : bool, optional
            Return a previous node if the tag cannot be found. By default False

        Returns
        -------
        str
            node ID

        Raises
        ------
        KeyError
            If tag cannot be found
        """
        if tag is None:
            tag = [None]
        elif isinstance(tag, str):
            tag = [tag]

        for tg in tag:
            if tg == "latest":
                return self.current()
            try:
                return self.tags[tg]
            except KeyError:
                pass

        if not allow_fallback:
            raise KeyError(f"could not find tag: {tag} in {self.tags}")

        try:
            return self.tags["transforms"]
        except KeyError:
            return self.tags["native"]

    def render(self) -> DAG:
        """create a DAG from the variable operations

        Returns
        -------
        DAG
        """
        return DAG(dag=self.operations, output=self.output)

    def store_output(self, tag: str | list[str] | None = None, custom_label: str | None = None):
        """append a node ID to the list of DAG outputs.

        Parameters
        ----------
        tag : str | list[str] | None, optional
            Add output from a tag instead of the current ID, by default None
        """
        if tag is not None:
            self.output.append(self.get_tag(tag))
        self.output.append(self.current(custom_label=custom_label))

    def update_tracked(self, tag: str):
        for tracked in self.tracked:
            tracked.update(tag, tracked(tag))

    def set_tracked_variables_to_tag(self, reuse_from_tag: str | list[str] | None):
        if reuse_from_tag is not None:
            try:
                tag = self.get_tag(reuse_from_tag)
            except KeyError:
                self.add_tag(
                    reuse_from_tag if isinstance(reuse_from_tag, str) else reuse_from_tag[0]
                )
                tag = self.current()
        else:
            tag = self.current()

        self.update_tracked(tag)

    def dag(
        self,
        dag: dict,
        reuse_from_tag: str | list[str] | None = None,
        variables: dict[str, Self] | None = None,
        allow_fallback: bool = True,
    ):
        """add a DAG to the list of operations

        Parameters
        ----------
        dag : dict
        reuse_from_tag : str | list[str] | None, optional
            start from the tag, by default None
        variables : dict[str, Self] | None, optional
            list of variables that may be used by the dag, by default None

        """

        if isinstance(dag["output"], list):
            if len(dag["output"]) > 1:
                raise ValueError(
                    f"only dags with a single output are supported, received {dag['output']}"
                )
            dag["output"] = dag["output"][0]

        # replace dag inputs with correct names.
        if variables:
            for node in dag["dag"]:
                new_args = []
                for arg in node["args"]:
                    if isinstance(arg, list):
                        arg = [
                            (
                                variables[a].get_tag(reuse_from_tag, allow_fallback=allow_fallback)
                                if a in variables.keys()
                                else a
                            )
                            for a in arg
                        ]
                    elif isinstance(arg, dict):
                        arg = {
                            key: (
                                variables[a].get_tag(reuse_from_tag, allow_fallback=allow_fallback)
                                if a in variables.keys()
                                else a
                            )
                            for key, a in arg.items()
                        }
                    else:
                        if isinstance(arg, str) and arg in variables:
                            arg = variables[arg].get_tag(
                                reuse_from_tag, allow_fallback=allow_fallback
                            )
                    new_args.append(arg)
                node["args"] = new_args

        # this may have already been done if self in variables
        try:
            input = self.get_tag(reuse_from_tag, allow_fallback=allow_fallback)
        except KeyError:  # computed variables won't necessarily have a previous state
            pass
        else:
            # update arguments to match input variable
            input_nodes = [el for el in dag["dag"] if self.name in el["args"]]
            for in_node in input_nodes:
                in_node["args"] = [input if self.name == x else x for x in in_node["args"]]

        # rename internal node edges to avoid collisions between pipelines
        # TODO: this doesn't properly handle kwargs but we can't simply do a replace like in args
        # due to operations such as xr.self.rename({"ST": "TAS"}) where the kwarg overlaps with args
        # but doesn't need replacement
        # NOTE: not clear if replacing kwargs would generally work anyway for dask,
        # see: https://github.com/dask/dask/issues/3741
        int_nodes = [el for el in dag["dag"] if self.name not in el["args"]]
        for node in int_nodes:
            name = node["name"]
            new_name = self.next(f"{name}")
            for sub_node in dag["dag"]:
                args = sub_node["args"]
                if name in args:
                    args[args.index(name)] = new_name
            node["name"] = new_name

            if name == dag["output"]:
                dag["output"] = new_name

        for process in dag["dag"]:
            self.operations.append(DAGProcess(**process))

    ##################################################################
    #   convenience functions provided for simplifying yaml format
    ##################################################################

    def add_op(
        self,
        function: str,
        args: list | None = None,
        kwargs: dict = {},
        short_name: str | None = None,
        reuse_from_tag: str | list[str] | None = None,
    ):
        """append an operation to the variable starting from the last node"""

        if not reuse_from_tag:
            input = [self.current()]
        else:
            input = [self.get_tag(reuse_from_tag)]
        output = self.next(short_name)
        if args is not None:
            input += args
        self.operations.append(
            DAGProcess(name=output, function=function, args=input, kwargs=kwargs)
        )

        if reuse_from_tag in [None, "latest"]:
            tag = "latest"
        else:
            tag = self.tags[reuse_from_tag]

        self.update_tracked(tag)

    def sort(self, sortby: str = "time", reuse_from_tag: str | list[str] | None = None):
        self.add_op("xr.self.sortby", kwargs={"variables": sortby}, short_name="sort")

    def open(
        self,
    ):
        """Use the variable loader to load the file into memory"""

        output = self.next("open")
        self.operations.append(
            DAGProcess(
                name=output,
                function=self.loader.function,
                args=self.loader.args,
                kwargs=self.loader.kwargs,
            )
        )

    def write(
        self,
        output_dir: str,
        reuse_from_tag: str | list[str] | None = None,
        filename: str | None = None,
        **kwargs,
    ):
        """
        Write the file to disk

        Parameters
        ----------
        output_dir: str
            path to the directory where the variable will be save
        reuse_from_tag: str (optional)
            tag to get the output_filename from. Defaults to current
        """

        if filename is None:
            if reuse_from_tag:
                tag = self.get_tag(reuse_from_tag, allow_fallback=True)
            else:
                tag = None

            if self.output_filename(tag) is None:
                tag = self.current()
                var_name = self.var_name(tag)
                self.output_filename.update(tag, f"{var_name}.nc")
                filename = self.output_filename(tag)
            else:
                filename = self.output_filename(tag)

        posix_path = (Path(output_dir) / filename).as_posix()
        input = [self.current(), posix_path]

        output = self.current("to_netcdf")
        self.operations.append(
            DAGProcess(
                name=output,
                function=self.writer.function,
                args=input,
                kwargs=self.writer.kwargs,
            )
        )
        # output = self.current("to_netcdf")
        # self.operations.append(
        #     DAGProcess(name=output, function="to_netcdf", args=input, kwargs=kwargs)
        # )
        self.store_output(custom_label="to_netcdf")
        return posix_path

    def rename(self, new_name: str, reuse_from_tag: str | list[str] | None = None):

        self.add_op("rename", args=[new_name], short_name="rename", reuse_from_tag=reuse_from_tag)
        self.output_filename.update(self.current(), f"{new_name}.nc")
        self.var_name.update(self.current(), new_name)

    def shift(self, shift: float | int, reuse_from_tag: str | list[str] | None = None):
        self.add_op("xr.add", args=[shift], short_name="shift", reuse_from_tag=reuse_from_tag)

    def scale(self, scale: float | int, reuse_from_tag: str | list[str] | None = None):
        self.add_op("xr.mul", args=[scale], short_name="scale", reuse_from_tag=reuse_from_tag)

    def divide(self, div: float | int, reuse_from_tag: str | list[str] | None = None):
        # it seems xarray doesn't do this automatically, so turn
        # scalar division into a multiplication for better speed.
        if isinstance(div, float) | isinstance(div, int):
            div = 1 / div
            op = "xr.mul"
        else:
            op = "xr.truediv"

        self.add_op(op, args=[div], short_name="divide", reuse_from_tag=reuse_from_tag)

    def resample(
        self,
        resolution: str,
        method: Literal["mean", "min", "max", "std"] = "mean",
        reuse_from_tag: str | list[str] | None = None,
    ):

        pandas_res_map = {
            "monthly": "MS",
            "daily": "1D",
            "yearly": "YS",
            "6hourly": "6H",
            "3hourly": "3H",
        }
        try:
            resolution = pandas_res_map[resolution]
        except KeyError:
            pass

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next(f"resample_{resolution}")
        self.operations.append(
            DAGProcess(
                name=output, function="xr.self.resample", args=[input], kwargs={"time": resolution}
            )
        )

        input = self.current()
        output = self.next(method)
        self.operations.append(DAGProcess(name=output, function=f"xr.self.{method}", args=[input]))

    def cycle(
        self,
        group: Literal["day", "month", "dayofyear"] = "month",
        method: Literal["mean", "min", "max", "std"] = "mean",
        reuse_from_tag: str | list[str] | None = None,
    ):

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next(f"groupby_{group}")
        self.operations.append(
            DAGProcess(
                name=output,
                function="xr.self.groupby",
                args=[input],
                kwargs={"group": f"{self.time_dim}.{group}"},
            )
        )
        self.time_dim = group

        input = self.current()
        output = self.next(method)
        self.operations.append(DAGProcess(name=output, function=f"xr.self.{method}", args=[input]))

    def persist(self, reuse_from_tag: str | list[str] | None = None):
        self.add_op("xr.self.persist", short_name="persist", reuse_from_tag=reuse_from_tag)

    def area_mean(self, reuse_from_tag: str | list[str] | None = None, **kwargs):

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next("area_mean")
        self.operations.append(
            DAGProcess(name=output, function=f"area_mean", args=[input], kwargs=kwargs)
        )

    def zonal_mean(self, reuse_from_tag: str | list[str] | None = None, **kwargs):

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next("zonal_mean")
        self.operations.append(
            DAGProcess(name=output, function=f"zonal_mean", args=[input], kwargs=kwargs)
        )

    def mask(
        self,
        mask: Self,
        reuse_from_tag: str | list[str] | None = None,
    ):
        self.add_op(
            "mask_where",
            args=[mask.get_tag(tag=reuse_from_tag, allow_fallback=True)],
            short_name="mask",
        )

    def cell_area(self, reuse_from_tag: str | list[str] | None = None, **kwargs):

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next("cell_area")
        self.operations.append(
            DAGProcess(name=output, function=f"cell_area", args=[input], kwargs=kwargs)
        )

    def from_formula(
        self,
        formula: str,
        variables: dict[str, Self],
        reuse_from_tag: str | list[str] | None = None,
    ):
        """Create a DAG from a formula string. Each variable should be the
        name of a variable in the stage. Brackets () can be used for order
        of operations.

        Parameters
        ----------
        formula : str
            Formula as a string
        variables : dict[str, Self]
            dictionary of variables that will be used to create the actual DAG.
            The keys should align with `var` in the formula str.
        reuse_from_tag : str | list[str] | None, optional
            If provided, the variable at `tag` is used, by default None

        """

        tree = ast.parse(formula)
        dag = AstParser().build_dag(tree)
        self.dag(dag, variables=variables, reuse_from_tag=reuse_from_tag)

    def branch_from_variable(self, variable: Self, reuse_from_tag: str | list[str] | None = None):
        output = self.next()
        tag = None
        if reuse_from_tag is not None:
            try:
                tag = self.get_tag(reuse_from_tag, allow_fallback=True)
            except KeyError:
                if isinstance(reuse_from_tag, list):
                    self.add_tag(reuse_from_tag[0])
                else:
                    self.add_tag(reuse_from_tag)
                tag = self.get_tag(reuse_from_tag, allow_fallback=True)

        # self.chunks.update(self.chunks.update(self.current(), self.chunks(tag)))
        self.operations.append(
            DAGProcess(
                name=output,
                function="rename",
                args=[variable.get_tag(reuse_from_tag, allow_fallback=True)],
                kwargs={"name": self.var_name(tag)},
            )
        )
