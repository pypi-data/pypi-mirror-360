.. overview

CanESM Pipelines
================

Writing a CanESM pipeline is equivalent to creating a :code:`DAG`, albeit often a large one with hundreds or thousands of nodes.
Manually creating these can be cumbersome and error prone so a simplified `YAML` representation is provided that allows
for easier composition and extension of :code:`DAG` elements. This simpler representation is tailored for CanESM processing
so is not as general as the :code:`DAG` format and aims to be a compromise between customizability and simplicity.

.. toctree::
   :maxdepth: 2
   
   pipelines
   stages
   example
   custom
   running
