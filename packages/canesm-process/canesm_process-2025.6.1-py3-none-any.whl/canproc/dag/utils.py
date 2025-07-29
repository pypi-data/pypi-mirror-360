from functools import partial
from typing import Callable
import numpy as np
import xarray as xr
from canproc import processors
from canproc.processors.xarray_ops import xarray_factory
import inspect
import operator
import builtins


_module_dict = {}


def register_module(
    module,
    prefix: str,
    func_factory: Callable | None = None,
    check_lookup: Callable | None = None,
):
    """
    Register a module so functions can be serialized and ran from that module.

    Parameters
    ----------
    module : module
        A new module to be registered
    prefix : str
        prefix for the module
    func_factory : Callable | None, optional
        If your module has function with wrappers, partials it may be
        necessary to write a custom `function_factory` to dispatch a function
        from string. If this is set `func_factory(name)` will be called for
        function dispatch, by default :code:`lambda name: getattr(module, name.split(".")[1])`
    check_lookup : Callable | None, optional
        Option function to use for matching modules with prefixes. By default :code:`lambda x: prefix == x`

    Examples
    --------
    >>> from canproc import register_module, DAG
    >>> from mypackage import mymodule
    >>> register_module(mymodule, 'mymod')
    >>> DAG(dag=[DAGProcess(name='data', function='mymod.myfunction', args=[1,2,3])], output='data')
    """

    if check_lookup is None:
        check_lookup = lambda x: prefix == x

    if func_factory is None:
        func_factory = lambda name: getattr(module, name.split(".")[1])

    _module_dict[prefix] = {
        "module": module,
        "function_factory": func_factory,
        "check_lookup": check_lookup,
    }


def serialize_function(func: Callable) -> str:
    """Given a function return a string name. This is the inverse to `function_factory`.

    Parameters
    ----------
    func : Callable
        function to be serialized

    Returns
    -------
    str
        name of the function including necessary modules
    """
    # TODO: How to extend this to arbitrary modules?

    if isinstance(func, partial):
        # _module_dict[inspect.getmodule(func.func).__name__]["function_serializer"](func)
        if "xarray" in inspect.getmodule(func.func).__name__:
            return f"xarray.self.{func.args[0]}"
    else:
        if hasattr(func, "__wrapped__"):
            if hasattr(func, "__wrapper__"):
                # _module_dict[func.__wrapper__]["function_serializer"](func)
                return f"{func.__wrapper__}.{func.__wrapped__.__name__}"
            return f"{inspect.getmodule(func).__name__}.{func.__name__}"
        # _module_dict[inspect.getmodule(func).__name__]["function_serializer"](func)
        if "xarray" in inspect.getmodule(func).__name__:
            return f"xarray.{func.__name__}"
        return f"{inspect.getmodule(func).__name__}.{func.__name__}"


def function_factory(name: str) -> Callable:
    """generate a function from a string name.

    Parameters
    ----------
    name : str
        name of the function. Use 'np.name' or 'xr.name' to load for numpy
        or xarray respectively. Use 'xr.add', 'xr.truediv' to apply an operation to
        two xarray objects.

    Returns
    -------
    Callable
        function

    Examples
    --------
    >>> function_factory('np.arange')
    >>> function_factory('xr.concat')
    >>> function_facotry('area_mean')
    """

    if "." in name:

        for prefix in _module_dict:
            if _module_dict[prefix]["check_lookup"](name.split(".")[0]):
                func = _module_dict[prefix]["function_factory"](name)
                break
        else:
            raise ValueError("module not recognize")

    else:

        try:
            func = getattr(processors, name)
        except:
            try:
                func = getattr(operator, name)
            except:
                func = getattr(builtins, name)

    return func


register_module(xr, "xr", xarray_factory, check_lookup=lambda module: module in ["xr", "xarray"])
register_module(np, "np", check_lookup=lambda module: module in ["np", "numpy"])
