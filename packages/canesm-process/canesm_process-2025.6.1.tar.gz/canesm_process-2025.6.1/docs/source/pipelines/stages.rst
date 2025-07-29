.. _stages:


Stages
------

A "stage" is a logical grouping of operations. Aside from the :code:`setup` stage, 
all stages apply a series of operations to a list of variables. Outputs from one stage 
may be used as inputs to following stages if desired by using the keyword :code:`reuse: stage_name`. 

A :code:`stage` has a few options:


Variables
*********

A list of variables to process in this stage. The variable name should correspond to a CanESM variable.

.. code-block:: yaml

    mystage:
      variables:
        - GT
        - ST


Applying Operations
*******************

.. note::

  Operations are applied after all other parts have completed. For example in the following:

  .. code-block:: yaml

    monthly:
      variables:
        GT: 
          shift: 273.15

  
  First monthly averaging is performed, then the values are shifted by :code:`273.15`. For linear operations
  this is generally more efficient, but can change results for non-linear operations. If an operation 
  should be performed before the :code:`monthly` calculation then it should be put in a previous stage.


DAG Format
^^^^^^^^^^
Operations can be applied to a variable using the :code:`DAG` format.

.. code-block:: yaml

    mystage:
      variables:
        - GT:
            dag:
              dag:
                - name: renamed
                  function: xr.self.rename
                  args: [GT]
                  kwargs:
                    GT: ST
                - name: initial_time
                  function: xr.self.isel
                  args: [renamed]
                  kwargs: 
                    time: 0
                - name: global_mean
                  function: xr.self.mean
                  args: [initial_time]  
              output: global_mean

This format provides the most flexibility for creating complex dags, but is often overkill for simple function calls.
For example, ince :code:`self` is specified in the function names we know what the first argument is.
Similarly, lists are ordered, so we know the order in which these are called, and assume we want the output of the final operation.
Therefore, a simplified version is also supported and equivalent to the above:

.. code-block:: YAML

    mystage:
      variables:
        - GT:
            dag:
              - function: xr.self.rename
                kwargs:
                  GT: ST
              - function: xr.self.isel
                kwargs: 
                  time: 0 
              - function: xr.self.mean

Shortcuts
^^^^^^^^^

Common operations can be applied using some keyword shortcuts. These are expanded internally to their :code:`DAG` representation so are equivalent.


.. code-block:: yaml

    mystage:
      variables:
        - GT:
          # convert to fahrenheit and rename to "ST"
            rename: ST
            scale: 1.8
            shift: 32


Computed Values
^^^^^^^^^^^^^^^

It is common to combine multiple CanESM variables into an output variable. 
As a shorthand these can be provided as a formula. For example, if we wanted 
to take the difference between a few monthly averaged fields we could write:


.. code-block:: yaml

    monthly:
      variables:
        - OLR
        - FSR
        - FSO
        - BALT: "FSO-FSR-OLR"


Formula parsing is based on python's :code:`ast` module, so most arithmetic syntax supported by python can be used.
For example, :code:`BALT: "2.4 * (FSO + FSR) - ((OLR - FSR) / (OLR + FSR))"` would be a valid (if meaningless) formula.
If additional operations need to be added to a computed variable this can be written as:


.. code-block:: yaml

  - BALT: 
      compute: "FSO-FSR-OLR"
      destination: null


.. note:: 

  As with other operations, computions are performed after the input variables have been transformed in the stage. 
  So in the example above, `BALT` is computed using the monthly average values of `FSO`, `FSR` and `OLR`. 


Masking Values
^^^^^^^^^^^^^^

We can create and apply masks using the :code:`mask` keyword. For example, lets say we want the monthly 
average of cloud tops for deep convection (:code:`TCD`). First, we need to mask the native data on the locations that
have deep convection, :code:`CDCB > 0`, then perform a monthly resampling of that masked data. To accomplish
this we use two stages: in the first stage we apply a mask to :code:`TCD` and in the second we take the monthly average
using this masked data.



.. code-block:: yaml

    setup:
      stages:
        - transforms
        - monthly

    transforms:
      variables:
        - CDCB
        - TCD:
            rename: CI
            mask: CDCB > 0

    monthly:
      reuse: transforms
      variables:
        - TCD



Branching from a Variable
^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it can be useful to branch a variable (think of this as a git branch) 
where we are spinning off a copy at a known point. This can be useful
if we want to keep both the original and a new version of the variable around 
for later modifications. As an example, in CMIP we need to save the same variable
twice, but with a different name. One way to accomplish that is through branching.


.. code-block:: yaml

    transforms:
      variables:
        - RH:
            rename: relative_humidity

    monthly:
      reuse: transforms
      variables:
        - RH
        - RH_clear_sky:
            branch: RH
            rename: relative_humidity_clear_sky



Setting Output Filenames
^^^^^^^^^^^^^^^^^^^^^^^^

Filenames can be changes using the `destination` keyword. 


.. code-block:: yaml

    transforms:
      variables:
        - RH:
            rename: relative_humidity
            destination: rh_no_mask.nc
        - BALT:
            compute: FSO - FSR - OLR
            destination: "top_of_atmosphere_flux.nc"


Saving files can also be turned off by setting destination to :code:`null`. This can be useful
for intermediate stages such as creating masks.

.. code-block:: yaml

    transforms:
      variables:
        - RH:
            rename: relative_humidity
            destination: rh_no_mask.nc
        - BALT:
            compute: FSO - FSR - OLR
            destination: null



Configuration Constants
^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it useful to define a constant that can be reused across files. Constants
are defined in the :code:`setup` stage, so any value defined here can be reused in other
stages by accessing them via :code:`${group.name}`

As an example, dask performance is highly dependent on chunk size, but optimizing 
this parameter also depends on the machine in use. To allow adjustment of chunks in a 
single place we can setup a variable 


.. code-block:: yaml

    setup:

      chunks:
        canam:
          gem_3d: {time: 8, lat: -1, lon: -1, level2: -1, level3: -1, level1: -1}
          gem_2d: {time: 96, lat: -1, lon: -1}


    monthly:
      reuse: daily
      variables:
        - CLD:
            rename: cls
            chunks: ${chunks.canam.gem_3d}
        - CICT:
            rename: clivi
            chunks: ${chunks.canam.gem_2d}