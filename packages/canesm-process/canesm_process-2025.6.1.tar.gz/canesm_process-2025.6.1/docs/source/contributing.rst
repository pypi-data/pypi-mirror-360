.. _contributing:

Contributing
------------

Setting up the repository
*************************

To contribute to canesm-processor, start by creating a fork of the main repository.  Go to https://gitlab.com/LandonRieger/canesm-processor 
and press the fork button on the top right.  This will create a copy of the repository in your local Gitlab namespace.

Your new fork will open and then you can clone the forked repository.  The command will look something like

.. code-block::

   git clone git@gitlab.com:YOURNAME/canesm-processor.git



Installing a Developer Version
******************************

It is recommended to create a fresh environment for development and install an editable 
copy of :code:`canesm-processor` into that environment. For :code:`conda` this looks like:

.. code-block::

    conda create -n canproc -c conda-forge python=$VERSION xarray numpy pandas dask pydantic pytest pytest-cov sphinx=8.0.2
    conda activate canproc
    pip install -e .[dev]


The :code:`[dev]` will install optional development dependencies such as those required to build the docs.


Developing a feature
********************

To create a new feature, you should work on a feature branch.  Ideally each branch is isolated to a single feature.  You can make a new branch with

.. code-block::

    git checkout -b shiny-new-feature


which will then create a new branch with the name `shiny-new-feature`.  The branch only exists on your local fork.
Don't worry about how many commits you make to the branch or how messy they are, when it is time to merge the branch into
the main repository all of the commits will be squashed into a single one and you will have the opportunity to write a new
description.

## Creating a pull request
Once you have made a commit to your branch and pushed the changes to your fork, you are ready to make a pull request.  This can
be done from the `pull requests` page on the main repository.  If your pull request is still a work in progress, prepend the title with `WIP:`

In addition to the feature, we require that all pull requests contain tests for the feature (if applicable), as well as updates to the documentation (if applicable)


Code Style
**********

For Python code we follow the `black <https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html>`_ code style.

For both we recommend using the provided pre-commit hook to automatically both format and check your code.  These can be installed with

.. code-block::
    
    pip install pre-commit


You can run the formatters manually by typing

.. code-block::

    pre-commit run -a


You will see output that looks like

.. code-block::
    
    black....................................................................Passed


If you want, you can then run

.. code-block::

    pre-commit install


which will set up the pre commit hooks to run automatically every-time you commit to the repository.

We highly recommend using the pre commit hooks. On every pull request these checks are automatically ran, and the code will not be merged in
if any fail.  Using the pre commit hooks locally saves everyone time.


Adding Docs
***********

Documentation is written in `sphinx <https://www.sphinx-doc.org/en/master/>`_ using reStructuredText and 
published via `GitLab Pages <https://docs.gitlab.com/ee/user/project/pages/>`_. You can build a local version
by running the following from the top level folder.


.. code-block::
    
    sphinx-build -b html docs/source docs/public

