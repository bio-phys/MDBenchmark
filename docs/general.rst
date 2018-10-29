Basic usage of MDBenchmark
==========================

Usage of MDBenchmark can be broken down into four points:

1. ``generate``
2. ``submit``
3. ``analyze``
4. ``plot``

We first generate benchmarks from an input file, e.g., ``.tpr`` in GROMACS.
Afterwards we submit all generated benchmarks to the queuing system of your HPC.
Finally, we analyze the performance of each run and generate a plot for easier
readability.

MDBenchmark currently supports two MD engines: `GROMACS`_ and `NAMD`_.
Extensions for `AMBER`_ and `LAMMPS`_ is planned and `help is appreciated`_. In
the following, we will describe the usage of the supported MD engines.

GROMACS
-------

Assuming your TPR file is called ``protein.tpr`` and you want to run benchmarks
with the module ``gromacs/2018.3``, run the following command:

.. code::

    mdbenchmark generate --name protein --module gromacs/2018.3

To run benchmarks on GPUs simply add the ``--gpu`` flag:

.. code::

    mdbenchmark generate --name protein --module gromacs/2018.3 --gpu

You can also create benchmarks for different versions of GROMACS:

.. code::

    mdbenchmark generate --name protein --module gromacs/2018.3 --module gromacs/2016.4 --gpu


NAMD
----

.. note::

  **NAMD support is experimental.** If you encounter any problems or bugs, we
  would appreciate to `hear from you`_.

Generating benchmarks for NAMD follows a similar process to GROMACS. Assuming
the NAMD configuration file is called ``protein.namd``, you will also need the
corresponding ``protein.pdb`` and ``protein.psf`` inside the same folder.

.. warning::

  Please be aware that all paths given in the ``protein.namd`` file
  must be absolute paths. This ensures that MDBenchmark does not destroy paths
  when copying files around during benchmark generation.

In analogy to the GROMACS setup, you can execute the following command to
generate benchmarks for a module named ``namd/2.12``:

.. code::

    mdbenchmark generate --name protein --module namd/2.12

To run benchmarks on GPUs add the ``--gpu`` flag:

.. code::

    mdbenchmark generate --name protein --module namd/2.12-gpu --gpu

Be aware that you will need to use different NAMD modules when generating and
running GPU and non-GPU benchmarks! To work with GPUs, NAMD needs to be compiled
separately and will be probably named differently on the host of your choice.
Using the ``--gpu`` option on non-GPU builds of NAMD may lead to poorer
performance and erroneous results.

Usage with multiple modules
---------------------------

You can use this feature to compare multiple versions of one MD engine or
different MD engines with each other. Note that the base name for the GROMACS
and NAMD files (see above) must to be the same, e.g., ``protein.tpr`` and
``protein.namd``::

    mdbenchmark generate --name protein --module namd/2.12 --module gromacs/2018.3

Steps after benchmark generation
--------------------------------

After you have generated your benchmarks, you can submit them to your queuing system::

    mdbenchmark submit

When benchmarks have finished, you can retrieve the performance results::

    mdbenchmark analyze

Finally, you can plot your benchmarks. For this you need to save your performance results to a CSV file via ``mdbenchmark analyze --save-csv results.csv`` and invoke the ``plot`` command on this file::

    mdbenchmark plot --csv results.csv

.. _GROMACS: http://www.gromacs.org/
.. _NAMD: https://www.ks.uiuc.edu/Research/namd/
.. _AMBER: http://ambermd.org/
.. _LAMMPS: https://lammps.sandia.gov/
.. _help is appreciated: https://github.com/bio-phys/MDBenchmark/issues/new
.. _hear from you: https://github.com/bio-phys/MDBenchmark/issues/new
