from canproc.dag import DAGProcess
from pathlib import Path
import logging
import yaml
from typing import Literal, Any, Callable
import re
import uuid
import ast
import numpy as np
import glob


class MergeException(ValueError):
    pass


OPERATION_MAP = {
    "+": "xr.add",
    "-": "xr.sub",
    "*": "xr.mul",
    "/": "xr.truediv",
    "**": "xr.pow",
    ">": "xr.gt",
    ">=": "xr.ge",
    "<": "xr.lt",
    "<=": "xr.le",
    "==": "xr.eq",
}


class UUID:

    def __init__(self):
        self.uuid = uuid.uuid4()

    @property
    def short(self):
        return str(self.uuid)[0:8]

    @property
    def long(self):
        return str(self.uuid)


def canesm_52_filename(input_dir: Path, variable: str) -> str:
    return (input_dir / "*_gs.001*").as_posix()


def canesm_6_filename(input_dir: Path, variable: str) -> str:
    # return (input_dir / "*" / f"{variable}.nc").as_posix()
    return (input_dir / f"{variable}.nc").as_posix()


def source_filename(format: str) -> Callable[[Path, str], str]:

    def filename(input_dir: Path, variable: str):
        return format.replace("{input}", input_dir.as_posix()).replace("{variable}", variable)
        # return glob.glob(fname)

    return filename


def get_name_from_dict(data: dict | str):
    if isinstance(data, str):
        return data
    # add check for multiple keys
    return list(data.keys())[0]  # probably don't need to create a list


def get_md_from_dict(metadata: dict, fill_defaults: bool = True):

    if fill_defaults:
        basic_md = ["units", "long_name"]
        for md in basic_md:
            if md not in metadata.keys():
                metadata[md] = "N/A"

    return metadata


def include_pipelines(config: Path) -> list[list | str]:
    """iteratively traverse yaml files to include nested pipelines

    Parameters
    ----------
    config : Path
        initial yaml file

    Returns
    -------
    list
        yaml file or list of yaml files found in config
    """

    source_dir = Path(config).parent.absolute()
    yaml_file = source_dir / config
    config = yaml.safe_load(open(source_dir / config))
    pipelines = []
    if "pipelines" in config:
        for pipeline in config["pipelines"]:
            pipelines.append(include_pipelines(source_dir / pipeline))
        return pipelines
    return yaml_file


def flatten_list(nested_list: list):
    """recursively flatten a list

    Parameters
    ----------
    nested_list : list
        list of list of list...

    Returns
    -------
    list
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def format_stages(pipeline: dict):
    """move keys from setup level down to stage level"""

    for stage in pipeline.keys():

        if stage == "setup":
            continue

        for key in ["encoding", "source", "loader"]:
            if key in pipeline[stage]:
                continue

            if key not in pipeline["setup"]:
                continue

            pipeline[stage][key] = pipeline["setup"][key]

    return pipeline


def default_var_name(variable: str | None = None) -> str:

    uuid = UUID()
    # if variable:
    # return f"{variable}-{uuid.short}"
    return f"{uuid.short}"


def format_dag_operation(dag: dict, self_arg: str | None = None) -> list[dict]:

    if "function" not in dag:
        raise ValueError(f"DAG element {dag} must provide a function name")

    fdag = dict(dag)

    if "args" not in dag:
        fdag["args"] = []

    # xr.self requires dataset passed as first argument, add if needed
    if ".self." in dag["function"] and fdag["args"] == []:
        fdag["args"] = [self_arg]

    if "name" not in dag:
        fdag["name"] = default_var_name()

    return fdag


def convert_shortform_dag(dag: dict[str, dict | list[dict]], variable: str | None = None):

    if isinstance(dag, list):
        longform = {"dag": list(dag)}
    elif isinstance(dag, dict):
        if "dag" not in dag:
            raise KeyError("dag should have the form {dag: [{...}, {...}, ...]}")
        longform = dict(dag)
    else:
        raise ValueError("{dag} is not in a recognizable format, should be a dictionary or list")

    self_arg = variable
    for idx, op in enumerate(longform["dag"]):
        longform["dag"][idx] = format_dag_operation(op, self_arg=self_arg)
        self_arg = longform["dag"][idx]["name"]

    if "output" not in longform:
        longform["output"] = longform["dag"][-1]["name"]

    if isinstance(longform["output"], str):
        longform["output"] = [longform["output"]]

    return longform


def format_variables(pipeline: dict):
    """move keys from the stage level to the variable level.
    This is to avoid collisions when merging stages from different files.

    Parameters
    ----------
    pipeline : dict


    Returns
    -------
    pipeline: dict
        input pipeline with "reuse" keys moved
    """

    for stage in pipeline.keys():

        if stage == "setup":
            continue

        # change computed variables in str format to dictionary format
        for idx, variable in enumerate(pipeline[stage]["variables"]):
            if isinstance(variable, str):
                pipeline[stage]["variables"][idx] = {variable: {}}
                continue

            name = get_name_from_dict(variable)
            if isinstance(variable[name], str):
                variable[name] = {"compute": variable[name]}
                pipeline[stage]["variables"][idx] = variable
                continue

            if "dag" in variable[name]:
                full_dag = convert_shortform_dag(variable[name]["dag"], name)
                variable[name]["dag"] = full_dag
                pipeline[stage]["variables"][idx] = variable

        for key in ["reuse", "resample", "encoding", "cycle", "area_mean", "source", "loader"]:

            if key not in pipeline[stage]:
                continue

            for idx, variable in enumerate(pipeline[stage]["variables"]):

                if isinstance(variable, str):
                    variable = {variable: {key: pipeline[stage][key]}}
                else:
                    name = get_name_from_dict(variable)

                    # computed variables are derived from resampled so don't resample again.
                    if (key == "resample" or key == "cycle") and "compute" in variable[name]:
                        continue
                    # if key == "cycle" and "compute" in variable[name]:
                    # continue

                    # don't overwrite variable values if they already exist
                    if key in variable[name]:
                        continue

                    variable[name][key] = pipeline[stage][key]

                pipeline[stage]["variables"][idx] = variable

            del pipeline[stage][key]

    return pipeline


def get_from_list(dct: dict, keys: list):
    for key in keys:
        dct = dct[key]
    return dct


def replace_constant(val, variables):
    if isinstance(val, str) and val[0:2] == "${":
        varname = val.split("${")[1].split("}")[0]
        val = get_from_list(variables, varname.split("."))
    return val


def replace_constants(config: dict | list, variables: dict):
    """
    In place replacement of templated variables in a `config` with the values in `variables`

    Parameters
    ----------
    config : dict
    variables : dict


    Examples
    --------

    >>> config = {'num_cores': '${system.cores}', launch: ${launch}}
    >>> variables = {'system': {'cores': 9}, 'launch': True}
    >>> config = replace_variables(config, variables)
    >>> {'num_cores': 9, launch: True}
    """

    if isinstance(config, dict):
        for key, val in config.items():
            if isinstance(val, dict) or isinstance(val, list):
                config[key] = replace_constants(val, variables)
            # elif isinstance(val, list):
            #     for element in val:
            #         element = replace_variables(element, variables)
            else:
                config[key] = replace_constant(val, variables)
    elif isinstance(config, list):
        for idx, element in enumerate(config):
            config[idx] = replace_constants(element, variables)
    else:
        config = replace_constant(config, variables)

    return config


def merge_lists(a, b):
    """
    merge two lists preserving order as best as possible
    """

    copy = [el for el in a]
    idx = 0
    previous_b = None
    for bidx, el in enumerate(b):
        # if element doesn't exist insert it at appropriate position
        try:
            idx = copy.index(el)
        except ValueError:
            copy.insert(idx + 1, el)
            idx += 1
    return copy


def merge_pipelines(a: dict, b: dict):
    """merge partial pipelines into a single pipeline

    Parameters
    ----------
    a : dict
    b : dict

    Returns
    -------
    dict
        merged pipeline

    Raises
    ------
    Exception
        dictionaries have overlap that cannot be safely merged
    """
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_pipelines(a[key], b[key])
            elif a[key] != b[key]:
                if isinstance(a[key], list) and isinstance(b[key], list):
                    a[key] = merge_lists(a[key], b[key])
                else:
                    raise Exception(f"Conflict at {key} with values {a[key]}, {b[key]}")
        else:
            a[key] = b[key]
    return a


def check_merge(d1: dict, d2: dict):
    """check if dictionaries are safe to merge and raise `ValueError` if not

    Parameters
    ----------
    d1 : dict
    d2 : dict
    name : str, optional
        used for error reporting

    Raises
    ------
    ValueError
        if dicts are not safe to merge.
    """

    if set(d1.keys()).isdisjoint(d2.keys()):
        return True

    overlap = list(set(d1.keys()) & set(d2.keys()))
    for key in overlap:
        if not d1[key] == d2[key]:
            raise MergeException(f"{key} appears with different values: {[d1[key], d2[key]]}")

    return True


def merge_destination(d1: dict, d2: dict, key: str = "destination", check_value: Any = None):
    """
    If `key` appears in only one of these dictionaries as `check_value` delete it.
    This is useful for removing default overrides.
    """

    if key in d1 and key not in d2:
        if d1[key] is check_value:
            del d1[key]

    if key in d2 and key not in d1:
        if d2[key] is check_value:
            del d2[key]


def merge_variables(vars: list[dict]):

    new_vars = []
    all_vars = [get_name_from_dict(v) for v in vars]

    # select unique, preserving order
    unique_vars = []
    for x in all_vars:
        if x not in unique_vars:
            unique_vars.append(x)

    for name in unique_vars:
        idx: list[int] = np.where(np.array(all_vars) == name)[0].tolist()
        if len(idx) > 1:
            tmp = vars[idx[0]][name]
            for i in idx[1:]:
                try:
                    check_merge(tmp, vars[i][name])
                except MergeException as e:
                    raise MergeException(f"Could not merge {name} due to: {e}")
                merge_destination(tmp, vars[i][name])
                tmp = tmp | vars[i][name]
            new_vars.append({name: tmp})
        else:
            new_vars.append(vars[idx[0]])

    return new_vars


def parse_formula(formula: str) -> list[str]:
    # checks left-most matches first so keep then first. E.g. test "<=" before "<"
    vars = [v.strip() for v in re.split("\\+|-|\\/|\\*|\\>=|\\>|\\<=|\\<|==", formula)]
    ops = [op.strip() for op in re.split("|".join(vars), formula) if op.strip()]
    return vars, ops


def check_dag_args_for_name(dag: dict, name: str, exact: bool = True) -> bool:
    """Check whether a particular value, `name` is present in the `dag` arguments.

    NOTE: this won't work if `args` contains a dictionary.

    Parameters
    ----------
    dag : dict
        dictionary representation of a dag
    name : str
        name to look for in args
    exact : bool, optional
        whether only exact mathces are allowed, by default True

    Returns
    -------
    bool
        whether `name` is the dag arguments

    """
    for node in dag["dag"]:
        for arg in flatten_list(node["args"]):
            if exact:
                if name == arg:
                    return True
            else:
                if name in str(arg):
                    return True
    return False


ast_ops = {
    ast.Pow: "**",
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.GtE: ">=",
    ast.Gt: ">",
    ast.LtE: "<=",
    ast.Lt: "<",
    ast.Eq: "==",
}


def parse_node(op: ast.AST, attr_name: Literal["left", "right"]):
    """_summary_

    Parameters
    ----------
    op : ast.AST

    attr_name : str
        attribute of the node, either "left" or "right"

    Returns
    -------
    str | float | int
    """
    side = getattr(op, attr_name)
    if isinstance(side, ast.Name):
        return side.id
    elif isinstance(side, ast.BinOp):
        return binary_op_to_name(side)
    elif isinstance(side, ast.Constant):
        return side.value


def binary_op_to_name(op: ast.AST):
    """Recursively convert an AST node to a string"""
    left = parse_node(op, "left")
    right = parse_node(op, "right")
    # replace '-' with long dash to avoid breaks in dask.
    return f"[{left}{ast_ops[type(op.op)]}{right}]".replace("-", "–")


def gen_formula_code(formula):
    fcode = "_"
    for c in formula.replace(" ", ""):
        if c.isalpha() or c.isnumeric():
            fcode += str(c)
        else:
            fcode += str(ord(c))
    return fcode


class AstParser(ast.NodeVisitor):
    """Parse formula into a DAG using the `ast` module

    Examples
    --------

    >>> import ast
    >>> parser = AstParser()
    >>> tree = ast.parse("A * 2.0 + B / (C + D)")
    >>> dag = parser.build_dag(tree)
    """

    def __init__(self):
        super().__init__()
        self._nodes = []

    def parse_node(self, op: ast.AST):

        if isinstance(op, ast.BinOp):
            return binary_op_to_name(op)
        elif isinstance(op, ast.Name):
            return op.id
        elif isinstance(op, ast.Constant):
            return op.value
        else:
            return op

    def generic_visit(self, node: ast.AST):

        if isinstance(node, ast.BinOp):

            left_name = self.parse_node(node.left)
            right_name = self.parse_node(node.right)
            self._nodes.append(
                {
                    "name": binary_op_to_name(node),
                    "function": OPERATION_MAP[ast_ops[type(node.op)]],
                    "args": [left_name, right_name],
                }
            )
        elif isinstance(node, ast.Compare):
            # NOTE: This assumes only a single comparator,
            # eg. A < B < C is not allowed
            left_name = self.parse_node(node.left)
            right_name = self.parse_node(node.comparators[0])
            self._nodes.append(
                {
                    "name": f"[{left_name}{ast_ops[type(node.ops[0])]}{right_name}]",
                    "function": OPERATION_MAP[ast_ops[type(node.ops[0])]],
                    "args": [left_name, right_name],
                }
            )

        super().generic_visit(node)

    def build_dag(self, tree: ast.AST) -> dict:
        """build a dag from an abstract syntax tree.

        Parameters
        ----------
        tree : ast.AST
            formula parsed into an abstract syntax tree.

        Returns
        -------
        dict
            dictionary compatible for conversion to `DAG`
        """
        self._nodes = []
        self.generic_visit(tree)
        return {"dag": self._nodes, "output": self._nodes[0]["name"]}
