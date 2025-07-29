.. canesm-processor documentation master file

canesm-processor
================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   gettingstarted
   pipelines/overview
   api/processors
   contributing

Overview
--------

CanESM Processor aims to support three main goals:

1. Collection of robust, basic processing elements for CanESM.
2. Support serialization of processing chains for interaction outside of python.
3. As far as is possible, decouple process logic from execution logic to support different computational environments (CPU, GPU or distributed) and storage formats (ccc, netcdf or zarr).


.. grid:: 3

    .. grid-item-card::  Getting Started
        :link: gettingstarted
        :link-type: doc

        Get started with the CanESM Processor including installation and basic concepts.

    .. grid-item-card::  CanESM Pipelines
        :link: pipelines/overview
        :link-type: doc

        Provides a :code:`YAML` interface for creating, composing and running multiple pipelines.

    .. grid-item-card::  API Reference
        :link: api/processors
        :link-type: doc

        The reference guide contains detailed descriptions of the CanESM processor API.


Relationship to other packages
------------------------------

:code:`canesm-processor` has overlap with a few other packages that may be better suited to your project depending on your use case.

ESMValTool
**********
ESMValTool is a great package for analysing CMIP 6 data and multimodel ensembles. It has a 
"preprocessor" that is similar in concept to the DAG graphs used here. However it has a few
key assumptions that work well for CMIP 6 data but that also make it less generalizable.

#. Data should be in CMOR format (or at least CMORizable).
#. Preprocessing is a linear pipeline (no branching/merging)
#. Preprocessing is limited to a specific set of :code:`ESMValTool` functions


:code:`canesm-processor` makes no assumptions about the format of the data being processed. You can
process :code:`ccc` or :code:`fstd` files just as well as CMORized netcdf. Additionally the "preprocessing" is not
limited to :code:`canesm-processor` functions, but can be user functions as well and include more general
program flow. The downside of this is that :code:`canesm-processor` can't assume folder structure, naming
conventions, file structure, etc, and so has to rely on the user to provide these.


Dask/Ray/Dagster/Cylc/etc
***************************************
These are largely engines that run data pipelines, but we can also use these packages to define 
the pipeline/DAG itself, so why use :code:`canesm-processor`? Typically, these packages have one or
more of these limitations:

#. It can be difficult to serialize a pipeline if we want to store it for later. This isn't always a concern, and the git repo could be considered the serialized version in some cases. However, if we want many small and composable pipelines this can be tricky with some of the packages.
#. Designed for problems where each step in the process creates a file that the next step picks up and processes. This can be a benefit if we need to restart pipelines in the middle of processing, or we're dealing with heavy computations and small files. However, if we have light compute and large files this I/O can become a bottleneck and we need a package that handles the pipeline communication in memory when desired.

:code:`canesm-processor` is meant as an abstraction over these pipeline engines, and you can choose a different engine
for a particular job depending on what works best. This works by defining the pipeline as a generic :code:`DAG`. This 
:code:`DAG` can then be converted to the format used by a particular engine for running. If you already have a working pipeline
in one of these frameworks :code:`canesm-processor` probably doesn't bring much to the table.
