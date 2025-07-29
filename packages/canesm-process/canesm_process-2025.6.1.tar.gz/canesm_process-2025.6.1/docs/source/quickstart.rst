.. quickstart

The Directed Acyclic Graph (DAG)
--------------------------------

A directed acyclic graph defines the program flow. Each node in the graph is a process to be ran, and each edge (the node connections) are the input and outputs of the process. Importantly, a DAG need not be a simple linear pipeline, but may include parallel branching and execution so long as it does not include a cycle (as this would cause infinite recursion)

A DAG Node
**********

As mentioned, a DAG node is simply a function we want to run on a set of inputs. As a simple example, lets say we want to load an array of numbers into memory. If we use ``np.arange`` for this our inputs will just be the length of the array. 

.. code-block:: python
   
   from canproc import DAGProcess
   proc = DAGProcess(name='make_array', function=np.arange, args=[8]),

The process ``name`` is important for defining the relation to other nodes as we'll see later. Generally, a ``function`` can be either a ``Callable`` object, such as python function, or a ``str`` object that can be used to generate a function, e.g. ``function="np.arange"`` would also work. As long as there is a one-to-one mapping between funtion names and functions the ``DAGProcess`` is serializable, allowing for easy storage and reuse. 

Combining Nodes for Data Pipelines
**********************************


.. grid:: 2

    .. grid-item::
        
        Nodes are linked via their input and outputs. The ``name`` of a process is 
        the output that can be used as input to other nodes. As a toy example lets 
        create 2 arrays using numpy, concatenate them, and then take an average. 
        The python code might look like this:

        .. code-block:: python

            import numpy as np
            arr1 = np.arange(8)
            arr2 = np.arange(0, 4)
            concat = np.concatenate([arr1, arr2])
            mean = np.mean(concat)


        This works fine, but the python code has drawbacks that ``canesm-processor`` aims to address:

        #. :code:`arr1` does not depend on :code:`arr2`, but the creation is done sequentially
        #. The process will run locally on the CPU which might not scale for large arrays.

    .. grid-item::

        .. mermaid::
            
            %%{init: {'theme':'neutral', 'look': 'handDrawn'}}%%
            graph
                S1[ ] --> |8| A["np.arange(8)"]
                S2[ ] --> |0, 4| B["np.arange(0, 4)"]
                B --> |arr1| C["np.concatenate(arr1, arr2)"]
                A --> |arr2| C
                C --> |concat| D["np.mean(concat)"]
                D --> |mean| E[ ]
                style E fill:#FFFFFF00, stroke:#FFFFFF00;
                style S1 fill:#FFFFFF00, stroke:#FFFFFF00;
                style S2 fill:#FFFFFF00, stroke:#FFFFFF00;



To create this structure in ``canesm-processor`` we would write:

.. code-block:: python

    import numpy as np
    from canproc import DAGProcess
    graph = [
        DAGProcess(name='arr1', function=np.arange, args=[8]),
        DAGProcess(name='arr2', function=np.arange, args=[0, 4]),
        DAGProcess(name='concat', function=np.concatenate, args=[['arr1', 'arr2']]),
        DAGProcess(name='mean', function=np.mean, args=['concat'])
    ]


Lastly, we define the ``output`` of the ``DAG``. This defines what edges of the graph we want to output. Typically this is the final output, but could be a list where intermediate steps are also returned. Putting this all together, we have the full DAG:

.. code-block:: python
   
   from canproc import DAG
   dag = DAG(dag=graph, output='mean')

