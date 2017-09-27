Benchmark Gromacs Simulations

Here we generate 10 benchmarks for protein with the gromacs module 5.1.4 on draco

.. code::

    benchmark generate --name protein --version 5.1.4 --top_folder 5.1.4 --host draco --max_nodes 10

To start the benchmarks give the top folder where we should look for benchmarks and 
tell the script it runs on draco.

.. code::

    benchmark start --top_folder 5.1.4 --host draco

Run a analysis script to produce a csv. Optional add --plot.

.. code::

    benchmark analyze --top_folder 5.1.4
