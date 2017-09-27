===================================
  Benchmark Gromacs Simulations
===================================

Here we generate 10 benchmarks for protein with the gromacs module 5.1.4.

.. code::

    benchmark generate --name protein --version 5.1.4 --max_nodes 10

The naming of the gromacs version assumes that you refer to the gromacs module
you are using. On our clusters this is always gromacs/-version-.

To run tests on the gpu add the --gpu flag

.. code::

    benchmark generate --name protein --version 5.1.4 --max_nodes 10 --gpu

You can also create benchmarks for different versions on gromacs

.. code::

    benchmark generate --name protein --version 5.1.4 --version 2016.3 --max_nodes 10 --gpu

After you generated all the benchmarks you want you can start them

.. code::

    benchmark start

Run a analysis script to produce a csv. Optional add --plot to give you the scaling behavior.

.. code::

    benchmark analyze


Notes
=====

The benchmark tool uses `mdsynthesis`_ to generate the folder sub structure for
each benchmark run. You can also use `mdsynthesis`_ in a python process later to
analyze the benchmarks and check that your proteins are stable

.. _mdsynthesis: https://mdsynthesis.readthedocs.io/en/master/
