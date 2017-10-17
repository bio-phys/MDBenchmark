===================================
  Benchmark GROMACS simulations
===================================

Generate, start and analyze benchmarks.


Installation
============

The package is currently under development. Refer to the installation wiki page for instructions.  


Usage
=====

Generate 10 benchmarks for our system with the gromacs module `5.1.4-plumed2.3`.

.. code::

    benchmark generate --name protein --version 5.1.4-plumed2.3 --max-nodes 10

The naming of the GROMACS version assumes that you refer to the GROMACS module
you are using. On our clusters this is always `gromacs/-version-`.

To run benchmarks on GPUs add the --gpu` flag:

.. code::

    benchmark generate --name protein --version 5.1.4-plumed2.3 --max-nodes 10 --gpu

You can also create benchmarks for different versions on GROMACS:

.. code::

    benchmark generate --name protein --version 5.1.4-plumed2.3 --version 2016.3 --max-nodes 10 --gpu

After you generated all the benchmarks, you can start them at once:

.. code::

    benchmark start

When the benchmark simulations have finished, you can run the analysis to
produce a `CSV` output file or a plot for direct usage (via `--plot` option).

.. code::

    benchmark analyze


Notes
=====

The benchmark tool uses `mdsynthesis`_ to generate the folder sub structure for
each benchmark run. You can also use `mdsynthesis`_ in a python process later to
analyze the benchmarks and check your simulations.

.. _mdsynthesis: https://mdsynthesis.readthedocs.io/en/master/
