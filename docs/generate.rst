Generation of benchmarks
========================

We first need to generate benchmarks with MDBenchmark, before we can run and
analyze these. All options for benchmark generation are accessible via
``mdbenchmark generate``. The options presented in the following text can be
chained together in no particular order in one single call to ``mdbenchmark
generate``. Before actually writing any files, you will be promted to confirm the action. You can skip this confirmation with the ``--yes`` option.

Specifying the input file
-------------------------

MDBenchmark requires one file to generate GROMACS benchmarks and three files for
NAMD. The base name of the input file is provided via the ``-n`` or ``--name``
option to ``mdbenchmark generate``. The following table lists all files required
by the given MD engine.

+------------------------+-------------------------------+
| MD engine              | Required files                |
+========================+===============================+
| GROMACS                | ``.tpr``                      |
+------------------------+-------------------------------+
| NAMD                   | ``.namd``, ``.psf``, ``.pdb`` |
+------------------------+-------------------------------+

If your input file is called ``protein.tpr``, then the base name of the file is
``protein`` and you need to call::

  mdbenchmark generate --name protein

Choosing a MD engine for the benchmark(s)
-----------------------------------------

MDBenchmark assumes that your HPC uses the `modules`_ package to manage loading
of MD engines. When given the name of a supported MD engine, it will try to find
the specified version::

  mdbenchmark generate --module gromacs/2018.3

It is also possible to specify two or more modules at the same time. MDBenchmark
will generate the correct number of benchmark systems for the respective MD
engines, sharing all other given options::

  mdbenchmark generate --module gromacs/2018.3 --module gromacs/2018.2

Also it is possible to mix and match MD engines in a single ``mdbenchmark
generate`` call, if the base name of the files is the same (see above)::

  mdbenchmark generate --module gromacs/2018.3 --module namd/2.12


Skipping module name validation
-------------------------------

If MDBenchmark does not manage to determine the naming of your MD engine
modules, it will warn you, but continue generating the benchmarks. Contrary, if
it manages to determine the naming, but is unable to find the specified version,
benchmark generation fails. If you are sure that the name is correct and
MDBenchmark is wrong, you can force the generation of benchmark systems with the
``--skip-validation`` option::

  mdbenchmark generate --skip-validation

Defining the number of nodes to run on
--------------------------------------

Benchmarks are especially helpful, if you want to figure out on how many nodes
you should run your MD job on. You can provide MDBenchmark with a range of nodes
to run benchmarks on. The two options defining the range are ``--min-nodes`` and
``--max-nodes`` for the lower and upper limit of the range, respectively. If you
do not specify either of these two options, MDBenchmark will use the default
values of ``--min-nodes=1`` and ``--max-nodes=5``. This would generate a total
of 5 benchmarks, running each benchmark on 1, 2, 3, 4 and 5 nodes.

Listing available hosts
-----------------------

MDBenchmark comes with two pre-defined templates for the MPCDF clusters `draco`_
and `hydra`_. You can easily create your own job templates, as described
:doc:`here </jobtemplates>`. You can list all available job templates via::

  mdbenchmark generate --list-hosts

Defining the job template to run from
-------------------------------------

MDBenchmark will try to lookup the hostname of your current machine and search
for a job template with the same name. If it cannot find the correct file or you
want to use one you have written yourself, e.g., named ``my_job_template``,
simply use the ``--host`` option::

  mdbenchmark generate --host my_job_template

Running on CPUs or GPUs
-----------------------

Depending on your setup you might want to run your simulations only on GPUs or
CPUs. You can do so with the ``--cpu/--no-cpu`` and ``--gpu/--no-gpu`` flags,
``-c/-nc` and ``-g/-ng`` respectively. If neither of both options is given,
benchmarks will be generated for CPUs only. The default template for the MPCDF
cluster ``draco`` showcases the ability to run benchmarks on GPUs::

  mdbenchmark generate --gpu

This generates benchmarks for both GPU and CPU partitions. If you only want to run on
GPUs this is easily achieved with::

  mdbenchmark generate --gpu --no-cpu


Using a different number of ranks or threads
--------------------------------------------

The correct choice on the number of MPI ranks and OpenMP threads and
hyperthreading depends on your available hardware and software resources, your
simulation system and used MD engine. MDBenchmark can help you scan different
numbers of ranks and threads.

.. note::

  The following was only tested with GROMACS.

To use this feature, you first need to know the number of physical cores on your
compute nodes. MDBenchmark will try to guess the number of physical cores. The
guess is only correct if the machine from which you submit the jobs, i.e., a
login node on a supercomputer, has the same number of cores as the actual
compute nodes. You can override the number of physical cores with the
``--physical-cores`` options.

In addition, Intel CPUs are able run two calculations on the same core at the
same time. This feature is called "hyperthreading". If your CPU supports
hyperthreading, then it also has logical cores, which is twice the number of
physical cores. Assuming the CPUs of your compute node have 40 physical cores
and supports hyperthreading, you need to specify the following settings::

  mdbenchmark generate --physical-cores 40 --logical-cores 80

The above example would generate benchmarks without hyperthreading. To enable
hyperthreading you need to specify the ``--hyperthreading`` option::

  mdbenchmark generate --hyperthreading

Now that you have defined the number of available cores and whether you want to
toggle hyperthreading, you can define the number of MPI ranks that MDBenchmark
should use for the job::

  mdbenchmark generate --ranks 2 --ranks 10 --ranks 40

The above command will generate jobs using 2, 10 and 40 MPI ranks. MDBenchmark
will calculate the number of OpenMP threads by itself. As a general rule:
`number_of_cores = number_of_ranks * number_of_threads`. If your CPU does not
support hyperthreading, then the number of cores equals the number of physical
cores. If it does support hyperthreading, then it equals the number of logical
cores.

Combining all options you can run benchmarks on 1-10 with and without GPUs using
either 4, 8 or 20 MPI ranks with hyperthreading with the following command::

  mdbenchmark generate --max-nodes 10 --cpu --gpu --ranks 4 --ranks 8 --ranks 20 --physical-cores 40 --logical-cores 80 --hyperthreading

In the above case, MDBenchmark will generate jobs with 4 MPI ranks/20 OpenMP
threads; 8 MPI ranks/10 OpenMP threads and 20 MPI ranks/4 OpenMP threads to
fulfill the constraint from above. A total of 60 benchmarks will be generated
(``10 (nodes) * 2 (gpu/cpu) * 3 (ranks)``).


Limiting the run time of benchmarks
-----------------------------------

You want your benchmarks to run long enough for the MD engine to stop optimizing
the performance, but short enough not to waste too much computing time. We
currently default to 15 minutes per benchmark, but think that common system
sizes (less than 1 million atoms) can be benchmarked in 5-10 minutes on modern
HPCs. To change the run time per benchmark, simply use the ``--time`` option::

  mdbenchmark generate --time 5

This would run all benchmarks for a total of five minutes.

Changing the job name
---------------------

If you want your benchmark jobs to have specific names, use the ``--job-name`` option::

  mdbenchmark generate --job-name my_benchmark

Multiple jobs per node
----------------------

.. note::

  Multiple simulations per node are currently only supported with GROMACS. The
  developers of MDBenchmark welcome all support to implement further MD engines.

It is possible to run multiple simulations on a single node to use the available
resources more efficiently. For example, when a node is equipped with two GPUs
it is possible to run either 1, 2 or 4 simulations on this single node. Each
instance of the simulation will generate shorter trajectories, but the overall
performance (the sum of all instances) will most likely be bigger than running a
single simulation on one node. This is especially useful when one is interested
in running many short simulations, instead of a single long simulation.

To use this feature, users can specify the ``--multidir`` option. This will make
use of the built-in functionality availabe in GROMACS, which itself will take
care of running multiple independent instances of the same system. The following
command will run four benchmarks of a single system on the same node::

  mdbenchmark generate --multidir 4

.. _modules: https://linux.die.net/man/1/module
.. _draco: https://www.mpcdf.mpg.de/services/computing/draco
.. _hydra: https://www.mpcdf.mpg.de/services/computing/hydra
