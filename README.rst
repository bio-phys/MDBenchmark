Benchmark Gromacs Simulations

Here we generate 10 benchmarks for protein with the gromacs module 5.1.4.

.. code::

    benchmark generate --name protein --version 5.1.4 --max_nodes 10

The naming of the gromacs version assumes that you refer to the gromacs module
you are using. On our clusters this is always `gromacs/-version-`.

To run tests on the gpu add the --gpu flag

.. code::

    benchmark generate --name protein --version 5.1.4 --max_nodes 10 --gpu

You can also create benchmarks for different versions on gromacs

.. code::

    benchmark generate --name protein --version 5.1.4 --version 2016.3 --max_nodes 10 --gpu

To start the benchmarks give the top folder where we should look for benchmarks and 
tell the script it runs on draco.

.. code::

    benchmark start

Run a analysis script to produce a csv. Optional add --plot.

.. code::

    benchmark analyze
