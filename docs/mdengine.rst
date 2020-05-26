Adding new MD engines
======================

If you need to add a new simulation engine to MDBenchmark that is not
yet supported, follow the steps below.

Set up local environment
------------------------

.. note::

  Make sure that you have `poetry`_ installed. We use it to provision the local
  development environment.

First, clone the ``git`` repository and enter the directory::

  git clone https://github.com/bio-phys/MDBenchmark.git
  cd MDBenchmark

.. _poetry: https://github.com/python-poetry/poetry

Install the development dependencies using ``poetry``::

  poetry install

You can now run ``mdbenchmark`` with ``poetry``::

  poetry run mdbenchmark

Create the new engine
---------------------

You can now add a new MD engine to the ``mdbenchmark/mdengines`` folder. Create
a file with the name of the engine, i.e., ``openmm.py``.

This new file must implement the functions ``prepare_benchmarks()`` and
``check_input_file_exists()``. For reference, refer to the paragraphs below and
the implementations of other engines.

``prepare_benchmarks()``
_________________________

This function extracts the filename (``md`` from ``md.tpr``) and copies the files required to run each
benchmark into the correct location. It receives the filename (``name``), i.e.,
``md.tpr`` and the relative path (``relative_path``) to the benchmark folder
about to be generated as arguments.

``check_input_file_exists()``
_____________________________

This function should assert that all files needed to run a benchmark with the
given engine exist. It receives the flename (``name``), i.e., ``md.tpr`` as
argument.

Add log file parser
-------------------

MDBenchmark needs to know how to extract the performance from the log file that
is produced by the MD engine. Therefore you need to add your engine to the
`PARSE_ENGINE` dictionary in ``mdbenchmark/mdengines/utils.py``.

The keys inside each engine dictionary have specific functions:

+--------------------+-------------------------------------------------------------------+
| Key                | Description                                                       |
+====================+===================================================================+
| performance        | Start of the line containing the performance                      |
+--------------------+-------------------------------------------------------------------+
| performance_return | A lambda function to extract the performance value                |
+--------------------+-------------------------------------------------------------------+
| ncores             | Start of the line containing the number of cores used for the run |
+--------------------+-------------------------------------------------------------------+
| ncores_return      | A lambda function to extract the number of cores                  |
+--------------------+-------------------------------------------------------------------+
| analyze            | A regular expression for the output file to parse                 |
+--------------------+-------------------------------------------------------------------+

Add cleanup exceptions
----------------------

Submitting a benchmark via ``mdbenchmark submit --force`` will delete all
previous results. You need to define all files that need to be kept in the
`FILES_TO_KEEP` dictionary in ``mdbenchmark/mdengines/utils.py``.

Register the engine
-------------------

Finally you need to register the engine with MDBenchmark. To do this, import the
engine in ``mdbenchmark/mdengines/__init__.py`` and add it into the
``SUPPORTED_ENGINES`` dictionary.
