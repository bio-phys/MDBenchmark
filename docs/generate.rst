Generation of benchmarks
========================

We first need to generate benchmarks with MDBenchmark, before we can run and
analyze these. All options for benchmark generation are accessible via
``mdbenchmark generate``. The options presented in the following text can be
chained together in no particular order in one single call to ``mdbenchmark
generate``.

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

  mdbenchmark generate --module gromacs/2016.4-plumed2.3

It is also possible to specify two or more modules at the same time. MDBenchmark
will generate the correct number of benchmark systems for the respective MD
engines, sharing all other given options::

  mdbenchmark generate --module gromacs/2016.4-plumed2.3 --module gromacs/2018.2

Also it is possible to mix and match MD engines in a single ``mdbenchmark
generate`` call, if the base name of the files is the same (see above)::

  mdbenchmark generate --module gromacs/2016.4-plumed2.3 --module namd/2.12


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
Depending on your cluster you might want to run your simulations on GPU nodes
or CPU only nodes. You can choose this with ``--cpu/--no-cpu`` or ``--gpu/--no-gpu`` flag.
By default mdbenchmark generate only runs on cpus but GPUs can be easily added.
The default template for the MPCDF cluster ``draco`` showcases the ability to
run benchmarks on GPUs. Generation of these benchmarks is possible with the
``-g`` or ``--gpu`` option::

  mdbenchmark generate --gpu

This generates benchmarks for both GPU and CPU partitions. If you only want to run on
GPUs this is easily achived by envoking::

   mdbenchmark generate --gpu --no-cpu


Limiting the run time of benchmarks
-----------------------------------

You want your benchmarks to run long enough for the MD engine to stop optimizing
the performance, but short enough not to waste too much computing time. We
currently default to 15 minutes per benchmark, but think that common system
sizes (less than 1 million atoms) can be benchmarked in 5-10 minutes on modern
HPCs. To change the run time per benchmark, simply use the ``--time`` option::

  mdbenchmark generate --time 5

This would run all benchmarks for a total of five minutes.

Mix and Match
-------------

All the above detailed commands can be used in any order and combined to
generate a large  set of desired benchmarks.
One can also generate them separately by invoking mdbenchmark for instance once
for each module one wishes to use.
Since under the hood a flexible data management system is used submitting and analyzing
them collectively is no problem. We use the highly versatile datreant library.


.. _modules: https://linux.die.net/man/1/module
.. _draco: https://www.mpcdf.mpg.de/services/computing/draco
.. _hydra: https://www.mpcdf.mpg.de/services/computing/hydra
