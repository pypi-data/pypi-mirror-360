.. _customize:

Extending canesm-processor
--------------------------

The simplest way to use your own code in :code:`canesm-processor` is to simply pass 
functions when setting up a DAG. For examples, lets say I have a function 
:code:`fancy_analysis` in my package :code:`awesome_stats` that I want to call as part of 
a pipeline. Then I can simply write

.. code-block:: python
   
   from canproc import DAGProcess
   from awesome_stats import fancy_analysis
   dag = DAG(
       dag=[
            DAGProcess(name='temperature', function='xr.open_mfdataset', args=['path/to/files/*/nc']),
            DAGProcess(name='output', function=fancy_analysis, args=['temperature']),
            DAGProcess(name='output_test', function=fancy_analysis, args=['temperature'], kwargs={'myoption': True})
           ],
       output=['output', 'output_test']
   )


This works, but if we want to write DAG templates or save a DAG for later, :code:`fancy_analysis` isn't serializable.
To handle this case, we need to tell :code:`canesm-processor` where your code is and what you want to call it. To do this
we use the :code:`register_module` function:

.. code-block:: python

   from canproc import register_module
   import awesome_stats
   register_module(awesome_stats, prefix='awst')


Now we can write DAGs in a serializable format so your function can be serialized or called externally.

.. code-block:: python
   
   from canproc import DAGProcess
   from awesome_stats import fancy_analysis
   dag = DAG(
       dag=[
            DAGProcess(name='temperature', function='xr.open_mfdataset', args=['path/to/files/*.nc']),
            DAGProcess(name='output', function='awst.fancy_analysis', args=['temperature']),
            DAGProcess(name='output_test', function='awst.fancy_analysis', args=['temperature'], kwargs={'myoption': True})
           ],
       output=['output', 'output_test']
   )