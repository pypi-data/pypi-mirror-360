from canproc.dag import DAG, DAGProcess, function_factory, serialize_function
from canproc.dag.dag import merge
from canproc.dag.utils import register_module
import importlib.metadata


__version__ = importlib.metadata.version("canesm-process")
