from canproc.pipelines.loaders import (
    FileLoader,
    FileWriter,
    create_loader,
    default_loader,
    create_writer,
)
from canproc.pipelines.utils import (
    flatten_list,
    format_variables,
    format_stages,
    get_name_from_dict,
    get_md_from_dict,
    include_pipelines,
    merge_pipelines,
    canesm_52_filename,
    canesm_6_filename,
    source_filename,
    parse_formula,
    check_dag_args_for_name,
    merge_variables,
    replace_constants,
    gen_formula_code,
    MergeException,
)
from canproc.pipelines.variable import Variable, FileLoader
from canproc import DAG, merge, DAGProcess
from pathlib import Path
import yaml
from collections import namedtuple
import warnings


MergedOutput = namedtuple("Output", ["node", "path"])

try:
    import h5netcdf

    NC_ENGINE = "h5netcdf"
except ImportError:
    NC_ENGINE = "netcdf4"


class Pipeline:
    """
    Convert a YAML configuration file to a DAG pipeline


    Example
    -------

    >>> from canproc.pipelines import Pipeline
    >>> pipeline = Pipeline('config.yaml', '/space/hall6/...', '/space/hall6/...')
    >>> dag = pipeline.render()

    """

    def __init__(
        self, config: str | Path, input_dir: str | Path, output_dir: str | Path | None = None
    ):
        """Pipeline initialization

        Parameters
        ----------
        config : str | Path
            path to the yaml configuration file
        input_dir : str | Path
            directory of input files
        output_dir : str | Path | None, optional
            top-level directory for output files, by default same as input directory.
            Sub-directories specified in `config` are relative to this location
        """

        # yaml.SafeLoader.add_constructor('None', lambda a : None)

        self.path = config
        self.config = yaml.safe_load(open(config, "r"))
        self.variables: dict[str, Variable] = {}
        self.stages: list[str] = []
        self.directories: dict[str, Path] = {}

        self.input_dir = Path(input_dir)
        if output_dir is None:
            self.output_dir = input_dir
        else:
            self.output_dir = Path(output_dir)

        self.file_lookup = (
            canesm_52_filename
            if self.config["setup"]["canesm_version"] == "5.2"
            else canesm_6_filename
        )

        self.directories = self.config["setup"]["output_directories"]
        for directory in self.directories:
            self.directories[directory] = self.output_dir / Path(self.directories[directory])

        self.merged_netcdf: dict[str, list[MergedOutput]] = {}
        if "output_filenames" in self.config["setup"]:
            for stage, filename in self.config["setup"]["output_filenames"].items():
                self.merged_netcdf[filename] = []

    def _include_pipelines(self):
        """Collect and merge all the sub pipelines"""

        if "pipelines" not in self.config:
            self.config = format_stages(self.config)
            self.config = format_variables(self.config)
            self.config = replace_constants(self.config, self.config["setup"])
            return

        pipelines = flatten_list(include_pipelines(self.path))

        del self.config["pipelines"]

        # first pass to get all the setup stages and merge them together
        # this is necessary so we can apply the setup to each pipeline stage
        setup = self.config["setup"]
        for pipeline in pipelines:
            pipeline = yaml.safe_load(open(pipeline, "r"))
            if "setup" in pipeline:
                setup = merge_pipelines(setup, pipeline["setup"])

        for pipeline in pipelines:
            pipeline = yaml.safe_load(open(pipeline, "r"))
            pipeline = format_stages(merge_pipelines(pipeline, {"setup": setup}))
            pipeline = format_variables(pipeline)
            self.config = merge_pipelines(self.config, pipeline)

        self.config = replace_constants(self.config, self.config["setup"])
        for stage in self.config:
            if "variables" in self.config[stage]:
                try:
                    self.config[stage]["variables"] = merge_variables(
                        self.config[stage]["variables"]
                    )
                except MergeException as e:
                    raise MergeException(f"Could merge {stage} due to: {e}")

    def _setup_stages(self):
        """Initialize the pipeline stages"""
        self.stages = self.config["setup"]["stages"]
        for stage in self.stages:
            if stage not in self.config:
                try:
                    self.stages.remove(stage)
                except ValueError:
                    pass

    def create_default_loader(self, filename: str, kwargs: dict) -> FileLoader:
        if "file_format" in self.config["setup"]:
            warnings.warn(
                "specifying `file_format` is deprecated and will be removed.",
                DeprecationWarning,
            )
            if "netcdf" in self.config["setup"]["file_format"].lower():
                engine = NC_ENGINE
            else:
                raise ValueError(
                    "If file_format is specified it must be 'netcdf', otherwise a custom `loader` is required"
                )
        else:
            engine = NC_ENGINE

        loader_kwargs = {
            "engine": engine,
            "parallel": True,
            "chunks": {"time": 96},
        }
        if "chunks" in kwargs:
            loader_kwargs["chunks"] = kwargs.pop("chunks")

        return default_loader(filename, kwargs=loader_kwargs)

    def _initialize_variable(self, stage: str, name: str, var: dict):
        from_file = True
        kwargs = {}

        # if its computed its always not from file,
        # this supersedes dag which may reuse the computed variable
        if "compute" in var[name] or "branch" in var[name] or isinstance(var[name], str):
            from_file = False

            if "branch" in var[name]:
                branch = var[name]["branch"]
                for v in self.config[stage]["variables"]:
                    key = list(v.keys())[0]
                    if key == branch:
                        if "chunks" in v[key]:
                            kwargs["chunks"] = v[key]["chunks"]

        elif "dag" in var[name]:
            from_file = check_dag_args_for_name(var[name]["dag"], name)

        if from_file:
            filename = (
                source_filename(var[name]["source"])(self.input_dir, name)
                if "source" in var[name]
                else self.file_lookup(self.input_dir, name)
            )
            if "loader" in var[name]:
                loader = create_loader(var[name]["loader"], filename)
            else:
                loader = self.create_default_loader(filename, var[name])
        else:
            loader = None

        if "writer" in var[name]:
            writer = create_writer(var[name]["writer"])
        else:
            writer = FileWriter("to_netcdf", args=[], kwargs={"engine": NC_ENGINE})

        self.variables[name] = Variable(name, loader=loader, writer=writer, **kwargs)

    def _initialize_variables(self):
        """
        Collect variables from all stages
        """

        for stage in self.stages:
            for var in self.config[stage]["variables"]:
                name = get_name_from_dict(var)

                # skip already created variables to preserve from_file information
                if name not in self.variables:
                    self._initialize_variable(stage, name, var)

            # order dictionary so computed operations occur last (e.g. resample monthly happens first).
            for var in self.config[stage]["variables"]:
                self.config[stage]["variables"].sort(
                    key=lambda x: self.variables[get_name_from_dict(x)].from_file, reverse=True
                )

    def _open_files(self):
        """
        Open all the necessary files
        """
        for var in self.variables.values():
            if var.from_file:
                var.open()
                var.add_tag("native")

    @staticmethod
    def parse_name_and_variable(var):
        if isinstance(var, dict):
            name = get_name_from_dict(var)
            variable = var[name]
        else:
            name = var
            variable = var
        return name, variable

    def _add_stage_to_variable(self, var: str | dict, stage: str):
        """Add a stage to a variable

        Parameters
        ----------
        var : str
            name of variable, or dictionary containing name as first key
        stage : str
            stage name
        """

        name, variable = self.parse_name_and_variable(var)
        tag = (
            variable["reuse"]
            if "reuse" in variable
            else ("native" if self.variables[name].from_file else None)
        )
        precomputed = False

        # specialized stages for variables
        if stage in ["daily", "monthly", "yearly", "6hourly", "3hourly"]:
            self.variables[name].resample(f"{stage}", method="mean", reuse_from_tag=tag)
            precomputed = True

        elif stage in ["annual_cycle"]:
            self.variables[name].cycle(group="month", method="mean", reuse_from_tag=tag)
            precomputed = True

        elif stage in ["rtd"]:
            self.variables[name].resample(resolution="yearly", reuse_from_tag="monthly")
            self.variables[name].add_tag("rtd:annual")
            self.variables[name].area_mean(reuse_from_tag="rtd:annual")
            precomputed = True

        elif stage in ["zonal"]:
            self.variables[name].zonal_mean(reuse_from_tag=tag)
            precomputed = True

        # general computation stages
        # if we added a computation (ie resample) we need to start the compute stage from there
        if precomputed:
            current = f"{stage}:precompute"
            self.variables[name].add_tag(current)
        else:
            current = tag
        self._add_stage_to_computation(var, stage, tag=current)

    def create_mask(self, formula: str, tag: list[str] | str | None = None, mask_tag: str = "mask"):
        vars, ops = parse_formula(formula)
        # update mask tag to include operations
        uid = gen_formula_code(formula.replace(" ", ""))
        mask_tag += uid

        var = self.variables[vars[0]]
        if mask_tag in var.tags:
            return var, mask_tag
        else:
            var.from_formula(formula, self.variables, reuse_from_tag=tag)
            var.add_tag(mask_tag)
            return var, mask_tag

    def _add_stage_to_computation(
        self, var: dict[str, dict], stage: str, tag: str | list[str] | None = None
    ):
        """Add a stage to a computation

        Parameters
        ----------
        var : str
            dictionary containing name as first key
        stage : str
            stage name
        tag : str | list[str] | None
            If provided, start the computation from this tag.
        """

        name, operations = self.parse_name_and_variable(var)
        variable = self.variables[name]

        # branch if needed before applying other operations
        if "branch" in operations:
            variable.branch_from_variable(
                self.variables[operations.pop("branch")], reuse_from_tag=tag
            )
            tag = "latest"

        for key in operations:
            if key == "compute":
                variable.from_formula(operations[key], self.variables, reuse_from_tag=tag)
                variable.rename(name, reuse_from_tag="latest")

            elif key == "dag":
                variable.dag(
                    operations[key],
                    reuse_from_tag=flatten_list([tag, "latest"]),
                    variables=self.variables,
                )

            elif key == "chunks":  # rechunk the variable if specified
                tag_ = variable.get_tag(tag)
                try:  # computed variables may not have tags yet
                    current_chunks = variable.chunks(tag_)
                except:
                    current_chunks = None
                if current_chunks != operations[key]:
                    variable.add_op(
                        function=f"xr.self.chunk",
                        kwargs={"chunks": operations[key]},
                        reuse_from_tag=tag,
                        short_name="chunk",
                    )
                    tag = "latest"

            elif key in variable.allowed_operations:
                # TODO: think about *args, **kwargs as inputs to avoid this if/else and make this more generic
                if key == "mask":
                    vars, ops = parse_formula(operations[key])
                    if len(ops) > 0:
                        mask_tag = f"mask_{stage}"
                        mask, mask_tag = self.create_mask(
                            operations[key], tag=tag, mask_tag=mask_tag
                        )
                        variable.mask(mask, reuse_from_tag=mask_tag)
                    else:
                        mask = self.variables[operations[key]]
                        variable.mask(mask, reuse_from_tag=tag)
                else:
                    if key in ["rename", "destination", "resample", "cycle"]:
                        arg = operations[key]
                    else:
                        # evaluate factor for computation
                        arg = operations[key]
                        if isinstance(arg, str):
                            try:
                                arg = float(arg)
                            except ValueError as e:
                                arg = eval(arg)

                    # destination should set the output at the current stage
                    if key == "destination":
                        tmp_tag = "latest"
                    else:
                        tmp_tag = tag

                    if key == "area_mean" or key == "cell_area":
                        if arg:  # check for area_mean: False
                            if isinstance(arg, dict):
                                getattr(variable, key)(**arg, reuse_from_tag=tmp_tag)
                            else:  # avoid passing True when `area_cell: True`
                                getattr(variable, key)(reuse_from_tag=tmp_tag)
                    else:
                        if isinstance(arg, dict):
                            getattr(variable, key)(**arg, reuse_from_tag=tmp_tag)
                        else:
                            getattr(variable, key)(arg, reuse_from_tag=tmp_tag)

            else:
                if key == "metadata":  # update metadata
                    # TODO: should we be using `assign_attrs` or merging dictionaries from previous stages?
                    variable.metadata = get_md_from_dict(operations[key])
                    continue  # don't update pointer to latest since we haven't added operation
                # keys that are option and not operations
                elif key in ["chunks", "reuse", "encoding", "source", "loader"]:
                    continue  # don't update pointer to latest since we haven't added operation
                else:
                    try:
                        # could be isel, mean, etc; any xarray Dataset operation
                        variable.add_op(function=f"xr.self.{key}", kwargs=operations[key])
                    except Exception as err:
                        raise err

            tag = "latest"  # subsequent operations should use values from this stage

        self.variables[name].add_tag(f"{stage}")

    def _write_and_tag(self, var: str | dict, stage: str):
        """
        Add a "to_netcdf" operation and store the output

        Parameters
        ----------
        var : dict
            either a variable name or a dictionary of {name: operations}
        stage : str
            name of the stage
        destination : str | None | bool, optional
            if a str used for the name of the file. If `None` default name is used. If `False` no file is written.
        """

        # check if writing is turned off for this stage
        if stage not in self.directories:
            return

        name, operations = self.parse_name_and_variable(var)
        reuse_tag = stage  # make sure we use the latest stage by default
        kwargs = {}

        # turn write off if destination is None
        if "destination" in operations and (
            operations["destination"] == "None"
            or operations["destination"] is False
            or operations["destination"] is None
        ):
            return

        destination = operations.pop("destination", None)

        if "encoding" in operations:
            self.variables[name].writer.kwargs["encoding"] = operations["encoding"]

        if "reuse" in operations:
            reuse_tag = flatten_list([reuse_tag, operations["reuse"]])

        if self.variables[name].metadata:
            self.variables[name].writer.kwargs["metadata"] = self.variables[name].metadata

        try:
            posix_path = self.variables[name].write(
                output_dir=self.directories[stage],
                reuse_from_tag=reuse_tag,
                filename=destination,
                **kwargs,
            )
        except KeyError as e:
            raise KeyError(f"Variable {name} could not be written due to key error: {e}")
            # pass
        else:
            # TODO: knowing that "to_netcdf" needs to be specified is pretty brittle
            if self.merged_netcdf and stage in self.config["setup"]["output_filenames"]:
                self.merged_netcdf[self.config["setup"]["output_filenames"][stage]].append(
                    MergedOutput(node=self.variables[name].current("to_netcdf"), path=posix_path)
                )

    def _build_dag(self):

        for stage in self.stages:
            for var in self.config[stage]["variables"]:
                name, operations = self.parse_name_and_variable(var)

                # prefer variables from this stage, otherwise use the previous
                tag = [
                    x for x in flatten_list([stage, operations.get("reuse", None)]) if x is not None
                ]
                self.variables[name].set_tracked_variables_to_tag(tag)

                # for "computed" variables don't reapply monthly, zonal, etc
                if (
                    "compute" in operations
                    or "branch" in operations
                    or isinstance(operations, str)
                    or (
                        "dag" in operations and not check_dag_args_for_name(operations["dag"], name)
                    )
                ):

                    self._add_stage_to_computation(var, stage, tag=tag)
                    self._write_and_tag(var, stage)
                    continue

                self._add_stage_to_variable(var, stage)
                self._write_and_tag(var, stage)

    def _merge_stages(self):
        return merge([v.render() for v in self.variables.values()], keep_intermediate=True)

    def _merge_netcdf_output(self):

        ops = []
        output = []
        for output_filename, inputs in self.merged_netcdf.items():
            input_files = [o.path for o in inputs]
            input_nodes = [o.node for o in inputs]
            output_file = self.output_dir / output_filename
            node_name = f"merge_netcdf_{output_file}"
            output.append(node_name)
            ops.append(
                DAGProcess(
                    name=node_name,
                    function="merge_netcdf",
                    args=[input_files, output_file, True, input_nodes],
                    kwargs={
                        "open_kwargs": {"engine": NC_ENGINE},
                        "write_kwargs": {"engine": NC_ENGINE},
                    },
                )
            )
        if ops:
            return DAG(dag=ops, output=output)
        return []

    def render(self) -> DAG:
        """render a DAG suitable for running

        Returns
        -------
        DAG

        """
        self._include_pipelines()
        self._setup_stages()
        self._initialize_variables()
        self._open_files()
        self._build_dag()
        dag = self._merge_stages()
        merge_dag = self._merge_netcdf_output()
        if merge_dag:
            dag = merge([dag, merge_dag])
        return dag


def canesm_pipeline(
    config: str | Path, input_dir: str | Path, output_dir: str | Path | None = None
):
    pipeline = Pipeline(config, input_dir, output_dir)
    return pipeline.render()
