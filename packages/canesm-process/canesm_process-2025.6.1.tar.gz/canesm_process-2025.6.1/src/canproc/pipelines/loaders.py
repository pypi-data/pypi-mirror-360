# from canproc.dag import DAGProcess


class FileLoader:

    def __init__(
        self,
        function: str = "open_mfdataset",
        args: list | None = None,
        kwargs: dict | None = None,
    ):
        """Simple interface to file loading function.

        Parameters
        ----------
        function : str, optional
            name of the function used to open a file, by default "open_mfdataset"
        args : list | None, optional
            list of arguments passed to the function, by default None
        kwargs : dict | None, optional
            dictionary of function keyword arguments, by default None
        """

        self.function = function
        self.args = args
        self.kwargs = kwargs


class FileWriter:

    def __init__(
        self,
        function: str = "open_mfdataset",
        args: list | None = None,
        kwargs: dict | None = None,
    ):
        """Simple interface to file loading function.

        Parameters
        ----------
        function : str, optional
            name of the function used to open a file, by default "open_mfdataset"
        args : list | None, optional
            list of arguments passed to the function, by default None
        kwargs : dict | None, optional
            dictionary of function keyword arguments, by default None
        """

        self.function = function
        self.args = args
        self.kwargs = kwargs


def create_loader(ops: dict | str, filename: str = None):
    """
    Create a FileLoader object. `source` in args will be replaced by `filename` if present.

    Parameters
    ----------
    ops: dict | str
       If `str` the name of the function used to open files. Otherwise a dictionary with parameters
       used to create a FileLoader
    filename: str
        filename passed as argument to `FileLoader.function`

    Returns
    -------
        FileLoader
    """

    # if only the function name is provided fill in the default filename arg
    if isinstance(ops, str):
        loader_args = {"function": ops}
        loader_args["args"] = ["source"]
    else:
        loader_args = ops

    # replace source with correct filename
    if "source" in loader_args["args"]:
        idx = loader_args["args"].index("source")
        loader_args["args"][idx] = filename

    return FileLoader(
        loader_args["function"],
        loader_args.get("args", None),
        loader_args.get("kwargs", None),
    )


def default_loader(filename: str = None, kwargs: dict = None):
    """
    Create a FileLoader object that uses `open_mfdataset` to open `filename`

    Parameters
    ----------
    filename: str
        filename passed as argument to `FileLoader.function`
    kwargs: dict
        dictionary of keyword arguments passed to `FileLoader.function`

    Returns
    -------
        FileLoader
    """

    loader_args = {"function": "open_mfdataset", "args": [filename]}

    if kwargs is not None:
        loader_args["kwargs"] = kwargs

    return FileLoader(
        "open_mfdataset",
        loader_args.get("args", None),
        loader_args.get("kwargs", None),
    )


def create_writer(ops: dict | str):
    """
    Create a FileWriter object.

    Parameters
    ----------
    ops: dict | str
       If `str` the name of the function used to open files. Otherwise a dictionary with parameters
       used to create a FileLoader
    filename: str
        filename passed as argument to `FileLoader.function`

    Returns
    -------
        FileLoader
    """

    # if only the function name is provided fill in the default filename arg
    if isinstance(ops, str):
        loader_args = {"function": ops}
        loader_args["args"] = []
    else:
        loader_args = ops

    return FileWriter(
        loader_args["function"],
        loader_args.get("args", []),
        loader_args.get("kwargs", None),
    )
