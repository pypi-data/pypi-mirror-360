.. _running:

Command Line Interface
----------------------

To run a pipeline you can use the command line utility :code:`canproc-pipeline`:



.. click:: canproc.cli:process_pipeline
   :prog: cancproc-pipeline
   :nested: full


Runner Considerations
*********************

For large pipelines, such as those used to processes CanESM output, the ``distributed`` 
scheduler is often the fastest. For ``ppp`` machines, where a full node is used to process
the data, it is often beneficial to set a large number of workers with 1 thread per worker.


.. code-block:: bash

    canproc-pipeline config.yaml /space/hall5... /space/hall5/... -w 40 -t 1
