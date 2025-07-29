.. _custom_functions:


User functions
==============


Writing a :code:`DAG` in the :code:`YAML` configuration file is fine for simple functions with 
one or two operations, but at some point we'll want more complicated processing. Let's say we want
to call a function :code:`weighted_average` from the package :code:`my_analysis`. 

#. Install the python package in the same environment as :code:`canesm-processor`.
#. Add our function call to the :code:`YAML` file
#. Register the package (or a specific package module) with :code:`canesm-processor`


Install the Package
-------------------
This is usually accomplished with :code:`pip install my_analysis` or :code:`conda install my_analysis`
after activating the appropriate conda environment. If this code isn't installable it must at least be 
accessible by the next step.


Add to YAML
-----------

.. code-block:: yaml
    :caption: my-pipeline.yaml

    monthly:
      variables:
        - OLR
        - FSR
        - FSO
        - BALT:
            dag:
              - function: myanalysis.weighted_average
                args: [OLR, FSR, FSO]


Register the Package
--------------------

Before running :code:`canesm_pipeline` register your code with :code:`register_module`. The :code:`prefix`
must match the value used in your pipeline file, in this example "myanalysis".

.. code-block:: python

   from canproc import register_module
   from canproc.pipelines import canesm_pipeline
   from canproc.runners import DaskRunner
   import my_analysis
   
   register_module(my_analysis, prefix='myanalysis')
   
   pipeline = canems_pipeline('my-pipeline.yaml')
   runner = DaskRunner()
   runner.run(pipeline) 
