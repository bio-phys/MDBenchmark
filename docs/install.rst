Installation inside an isolated environment
===========================================

Installing a new python package into the main python environment of your system
can lead to unforeseen consequences. Python packages can have dependencies on
different versions of the same package, i.e. ``numpy``. If package ``packageA``
depends on ``numpy==1.9.2`` and you install ``packageB``, which depends on
``numpy==1.14.1``, then ``packageA`` may stop to work. Isolating packages into
their own environments makes sure to provide the needed dependencies, while not
disrupting other the dependencies of other packages (in other environments).

Depending on your setup, there are different ways to create an isolated
environment. In the normal Python world, one calls them `virtual environment`_,
while users of the Anaconda distribution know them as `conda environment`_.

We recommend to install the package inside a `conda environment`_, while the
other ways are also supported.

Install via ``conda``
---------------------

This can easily be done with ``conda``. The following commands create an
environment called ``benchmark`` and then installs ``mdbenchmark`` inside of it.

.. code::

    $ conda create -n benchmark
    $ conda install -n benchmark -c conda-forge mdbenchmark

Before every usage of ``mdbenchmark``, you need to first activate the conda
environment via ``source activate benchmark``. After doing this once, you can
use ``mdbenchmark`` for the duration of your shell session.

.. code::

   $ source activate benchmark
   # mdbenchmark should now be usable!
   $ mdbenchmark
   Usage: mdbenchmark [OPTIONS] COMMAND [ARGS]...

     Generate and run benchmark jobs for GROMACS simulations.

   Options:
     --version  Show the version and exit.
     --help     Show this message and exit.

   Commands:
     analyze   analyze finished benchmark.
     generate  Generate benchmark queuing jobs.
     submit    Start benchmark simulations.

.. _virtual environment: https://google.com
.. _conda environment: https://conda.io/docs/user-guide/tasks/manage-environments.html

Install via ``pip``:
--------------------

Installation with `pip`
