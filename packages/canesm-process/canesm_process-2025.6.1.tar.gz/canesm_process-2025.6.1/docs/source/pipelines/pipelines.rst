.. pipelines


Pipeline Overview
-----------------

A pipeline is organized into :code:`stages`. Each option at the base 
level of a :code:`YAML` file is treated as a "stage". The only required 
stage is :code:`setup`. For more detailed information on stage options 
see :ref:`stages`


:code:`setup` Stage
*******************
Defines the directory structure, high level information like model version 
and the order in which the following :code:`stages` are evaluated.


Output directories
^^^^^^^^^^^^^^^^^^

Output directories are specified relative to the input directory.

.. code-block:: YAML

    setup:

      # defines where the output files for each stage will be written too.
      output_directories:
        monthly: "diags/monthly"
        daily: "diags/daily"
        rtd: "diags/rtd"
        variability: "diags/landon"



.. note::

   If a stage is not present in :code:`output_directories` the variables created in that stage will not be written to disc.


Loading Data
^^^^^^^^^^^^

Input Files
"""""""""""
By default input files are expected to be in a flat directory in ``input_dir`` with filenames of ``{input}/{variable}.nc``. 
This can be customized using the ``source`` keyword. As with ``encoding``, the value of ``source`` is propagated to variables in each stage.
If ``source`` is set at the ``stage`` or ``variable`` level, the lower level value will take precedent.
For example, if most of our input files are organized in monthly folders, expect for some land variables we could write our configuration as:

.. code-block:: YAML

    setup:

      # defines the format to look for input files {input} and {variable} will be replaced dynamically.
      source: "{input}/*/{variable}.nc"

    monthly:

       variables:
         - GT
         - BEG
         - ST:
             source: "{input}/land/CLASSIC_{variable}.nc"


Custom Loaders
""""""""""""""
By default ``xarray``'s ``open_mfdataset`` is used to open files, but if you would like to use other methods this can be overwritten. 
If a name of a function is provided then the source will be passed to this function. If additional arguments or kwargs are required 
these should be set using ``args`` and ``kwargs``. If a filename is expected then it should be passed as an arg and ``source`` will 
be dynamically replaced.

.. code-block:: YAML

    setup:

      # defines the format to look for input files {input} and {variable} will be replaced dynamically.
      source: "{input}/*/{variable}.nc"

    monthly:

       variables:
         - ST:
             source: "{input}/land/CLASSIC_{variable}.001"
             loader: mymodule.load_ccc
         - GT: 
             loader:
               function: xr.open_mfdataset
               args: [source]  # uses the default source specified on setup
               kwargs:
                 engine: netcdf4
                 decode_times: false
                 parallel: false


General information
^^^^^^^^^^^^^^^^^^^

.. code-block:: YAML

    setup:
      # general options that may affect how we process yaml->dag
      canesm_version: "6.0"


Ordering Stages
^^^^^^^^^^^^^^^
This defines the order in which :code:`stages` are executed. For example, we may want to reuse data from the daily stage when
computing the monthly averages, in this case we could write:

.. code-block:: YAML

    setup:
      stages:
        - daily
        - monthly


If no data is reused between stages then this section can be omitted.


Reusing Stages
^^^^^^^^^^^^^^
To reuse results from a previous stage, the `reuse` keyword can be used

.. code-block:: YAML

    setup:
      stages:
        - transforms
        - daily
        - monthly

    transforms:
      variables:
        - GT:
            rename: TS

    daily:
      reuse: transforms
      variables:
        - GT

    monthly:
      reuse: daily
      variables:
        - GT
        - ST


This will tell the :code:`daily` stage to use the variables from the output of 
the :code:`transforms` stage and the :code:`monthly` stage to use the variables from 
the output of the :code:`daily` stage. This will be applied to all variables in 
the stage in this file. Variables that are not defined in prior stages, e.g. :code:`ST` here,
will fallback to earlier stages, in this case the raw data loaded from disc. If multiple stages
are reused a list can be provided e.g.: :code:`reuse: [transforms, monthly]`


Resampling Stages
*****************

Resampling stages take variables and aggregrates them into coarser time bins. Currently the following stages are supported:

 - 3hourly
 - 6hourly
 - daily
 - monthly
 - yearly


.. code-block:: YAML
    
    # compute the monthly mean of `GT` and `ST` variables
    monthly:
      variables:
        - GT
        - ST


Custom Resampling
^^^^^^^^^^^^^^^^^

Additional resampling options can also be applied to all variables in a stage using the :code:`resample` keyword.
If we wanted to do a 3-day average we could use

.. code-block:: YAML

    custom_stage:
      resample: 3D
      variables:
        - ST
        - GT

By default this will peform a mean, but :code:`min`, :code:`max` or :code:`std` are also supported.

.. code-block:: YAML

    custom_stage:
      resample:
        resolution: 3D
        method: std
      variables:
        - ST
        - GT


Cycle Stages
************

Cycling stages take variables and aggregrates them into coarser time bins. Currently the following stages are supported:

 - annual_cycle


.. code-block:: YAML

    # compute the monthly annual cycle of `GT` and `ST` variables
    annual_cycle:
      variables:
        - GT
        - ST


Custom Cycles
^^^^^^^^^^^^^

Additional cycle options can also be applied to all variables in a stage using the :code:`cycle` keyword.
If we wanted to do a daily annual cycle we could use

.. code-block:: YAML

    custom_stage:
      cycle: dayofyear
      variables:
        - ST
        - GT

By default this will peform a mean, but :code:`min`, :code:`max` or :code:`std` are also supported.

.. code-block:: YAML

    custom_stage:
      cycle:
        group: dayofyear
        method: std
      variables:
        - ST
        - GT


:code:`rtd` Stage
*****************
A default RTD stage that converts variables to yearly global average values.

.. code-block:: YAML

    # compute the global, annual mean of `GT` and `ST` variables
    rtd:
      variables:
        - GT
        - ST


Custom Stages
*************
Users can create their own stages. These do not perform any operations by default except saving the ouptut to a file.
Instead, users can provide function names, arguments and keyword arguments that are constructed into a :code:`DAG`. 
Most parameters are optional, but in the complete form:

.. code-block:: YAML

    # compute monthly standard deviation of the `GT` variable
    variability:
      variables:
        - GT:
            dag:
              dag:
                - name: resampled
                  function: xr.self.resample
                  args: [GT]
                  kwargs:
                    time: MS
                - name: monthly_std
                  function: xr.self.std
                  args: [resampled]
              output: monthly_std


If you would like to call your own functions in a pipeline, see :ref:`custom_functions`.


NetCDF4 Encoding
****************

If you want to write the netcdf files using a particular encoding this can be done at the variable, stage or 
setup level, depending on the scope you would like it to apply. In the example below we specify the default encoding
as :code:`float32` with a :code:`_FillValue` of :code:`1.0e20`. Unless otherwise specified variables will be written
with this encoding (e.g. the daily :code:`ST` variable). The :code:`monthly` stage 
overwrites this and sets a new default, so the monthly variables (e.g. :code:`ST`) will have this encoding. Lastly, if we want a
specific encoding for the monthly, variable, :code:`GT` we can set this at the variable level.

.. code-block:: YAML

    setup:
      ...
      encoding:
        dtype: float32
        _FillValue: 1.0E+20  # note yaml format requires both a "." and a "+" to be read as a float

    monthly:
      reuse: daily
      encoding:
        dtype: float64
        _FillValue: -999
      variables:
        - ST
        - GT:
            encoding: 
              dtype: float64
              _FillValue: 1.0E+20

    daily:
      variables:
        - ST


Variable Attributes
*******************

By default, the output variables are assigned a `long_name` and `units` attribute. You can specify the desired values
by listing them in the YAML configuration; otherwise, they will be listed as "N/A". Additional attributes can also be listed
under the `metadata` key. The minimum and maximum values in the data array can also be added as an attribute by adding
the keys `min/max: True`.

.. code-block:: YAML

    setup:
      ...

    monthly:
      reuse: daily
      variables:
        - GT:
            metadata:
              long_name: "Monthly mean ground temperature aggregated over all tiles"
              units: "K"
              min: True
              max: True
              project: CMIP
