.. running

Running a DAG
-------------

The DAG defines the processes that need to be ran, the inputs and outputs and their relationships, 
but is agnostic on how this is executed. For that we use a ``Runner``. A simple runner that works 
well with netcdf, xarray and numpy is ``dask``. To process our dag using dask:

.. code-block:: python
   
   from canproc.runners import DaskRunner
   runner = DaskRunner()
   output = runner.run(dag)


For larger jobs with many nodes that can run in parallel the ``DaskDistributedRunner`` provides more 
control on the number of workers and threads. However, be aware that memory is equally distributed among
workers, so chunk sizes may need to be adjusted accordingly.


.. code-block:: python
   
   from canproc.runners import DaskDistributedRunner
   runner = DaskDistributedRunner(workers=40, threads_per_worker=1)
   output = runner.run(dag)
