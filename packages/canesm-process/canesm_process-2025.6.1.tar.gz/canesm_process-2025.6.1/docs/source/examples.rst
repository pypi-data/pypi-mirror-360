.. _examples:

Putting it together
-------------------

So far this has been a complicated (and slow) way to compute the mean of some small arrays, 
so let's look at a real example where we compute ENSO from a model run. Since this is 
essentially a linear pipeline we could write this as a single python function,
but this shows the ability to compose dags, and utilize xarray functionality. First, we
create some json files that define the different processes we want to apply:


.. tabs::

    .. tab:: Load Data

        .. code-block:: json
            :caption: load_region_data.json

            {
                "dag": [
                    {
                        "name": "data",
                        "function": "xr.open_mfdataset",
                        "args": ["input_file"],
                        "kwargs": {"engine": "netcdf4", "parallel": true}
                    },
                    {
                        "name": "region_data",
                        "function": "select_region",
                        "args": ["data"],
                        "kwargs": {"region": {"lat": [-10, 10], "lon": [120, 300]}}
                    }
                ],
                "output": "region_data"
            }

    .. tab:: Monthly Anomaly

        .. code-block:: json
            :caption: monthly_anomalies.json

            {
                "dag": [
                    {
                        "name": "grouped",
                        "function": "xr.self.groupby",
                        "args": ["region_data"],
                        "kwargs": { "group": "time.month" }
                    },
                    {
                        "name": "clim",
                        "function": "xr.self.mean",
                        "args": ["grouped"]
                    },
                    {
                        "name": "monthly_anom",
                        "function": "xr.sub",
                        "args": ["grouped", "clim"]
                    }
                ],
                "output": "monthly_anom"
            }

    .. tab:: ENSO

        .. code-block:: json
            :caption: enso.json

            {
                "dag": [
                    {
                        "name": "anomaly",
                        "function": "area_mean",
                        "args": ["monthly_anom"]
                    },
                    {
                        "name": "rolling",
                        "function": "xr.self.rolling",
                        "args": ["anomaly"],
                        "kwargs": { "time": 3, "center": true, "min_periods": 1 }
                    },
                    {
                        "name": "enso",
                        "function": "xr.self.mean",
                        "args": ["rolling"]
                    }
                ],
                "output": "enso"
            }
    
    .. tab:: Write netcdf

        .. code-block:: json
            :caption: to_netcdf.json

            {
                "dag": [
                    {
                        "name": "result",
                        "function": "xr.self.to_netcdf",
                        "args": "enso",
                        "kwargs": {"path": "enso.nc"}
                    }
                ],
                "output": "result"
            }


Now we have a set of procedures we can apply to some data in a variety of ways:


Python
******

.. code-block:: python

    from canproc import DAG, merge
    from canproc.runners import DaskRunner
    import json

    # Generate a DAG from the JSON files
    dags = []
    for file in ["load_region_data.json", "monthly_anomalies.json", "enso.json", "to_netcdf.json"]:
        dags.append(DAG(**json.load(open(file, "r"))))
    dag = merge(dags)

    # run the DAG using dask
    runner = DaskRunner()
    runner.run(dag)


Command Line
************

This can be ran from the command line using:

.. code-block:: bash

    canproc-run "load_region_data.json" "monthly_anomalies.json" "enso.json" "to_netcdf.json"


Remote Procedure Calls
**********************

Or, if we wanted we could spin up a small web server so we could compute DAGs remotely. 
For FastAPI, a simple endpoint might look like:


.. tabs::

    .. tab:: Backend

        .. code-block:: python

            @app.post("/dag")
            async def run_dag(dag: DAG):

                runner = DaskRunner("threads")
                return runner.run(dag)

    .. tab:: Frontend

        .. code-block:: javascript

            const dag = {}  // code to load or generate the json goes here.

            const res = await fetch(
                `http://${url}/dag`, 
                {
                    method: 'POST',
                    headers: {
                        Accept: 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(dag)
                }
            );
            const data = await res.json();


.. note::
    
    This is more useful if you have something like ``to_geojson`` as the final stage of the ``DAG`` instead of ``to_netcdf``.
    See :ref:`Extending canesm-processor <customize>` for more information on how to include your own functions.