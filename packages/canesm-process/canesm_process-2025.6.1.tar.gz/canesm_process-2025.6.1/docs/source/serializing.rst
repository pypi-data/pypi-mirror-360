.. serializing


Serializing and Composing DAGs
------------------------------

If we just wanted to write functions that could be ran in a DAG, we wouldn't need ``canesm-processor``. One of the goals of this
work is to allow for a ``DAG`` to be serializable so they can be easily stored, templated and composed into larger transforms without needing to 
worry about execution details.

JSON Format
***********

DAGs can be represented as JSON blocks

.. tabs::

    .. tab:: JSON

        .. code-block:: JSON
            :caption: compute_mean.json

            {
                "dag": [
                    {
                        "name": "arr1",
                        "function": "np.arange",
                        "args": [8],
                    },
                    {
                        "name": "arr1",
                        "function": "np.arange",
                        "args": [0, 4],
                    },
                                {
                        "name": "concat",
                        "function": "np.concatenate",
                        "args": [["arr1", "arr2"]],
                    },
                    {
                        "name": "mean",
                        "function": "np.mean",
                        "args": ["concat"],
                    }
                ],
                "output": "mean"
            }

    .. tab:: Python

        .. code-block:: python

            import numpy as np
            from canproc import DAGProcess, DAG
            dag = DAG(dag=[
                            DAGProcess(name="arr1", function=np.arange, args=[8]),
                            DAGProcess(name="arr2", function=np.arange, args=[0, 4]),
                            DAGProcess(name="concat", function=np.concatenate, args=[["arr1", "arr2"]]),
                            DAGProcess(name="mean", function=np.mean, args=["concat"])
                        ],
                    output="mean"
            )