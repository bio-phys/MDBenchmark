Defining host templates
=======================

You can create your own host templates in addition to the ones shipped with the
MDBenchmark. We use the ``jinja2`` Python package for these host templates.
Please refer to the `official Jinja2 documentation <http://jinja.pocoo.org/>`_
for further information on formatting and functionality.

To be detected automatically, a template file must have the same filename as
returned by the UNIX command ``hostname``. If this is not the case, you can
point MDBenchmark to a specific template by providing its name via the
``--host`` option.

Assuming you created a new host template in your home directory ``~/.config/MDBenchmark/my_custom_hostfile``::

    mdbenchmark generate --host my_custom_hostfile

Sun Grid Engine (SGE)
---------------------

This example shows a HPC running SGE with 30 CPUs per node.

.. code::

  #!/bin/bash
  ### join stdout and stderr
  #$ -j y
  ### change to currend work dir
  #$ -cwd
  #$ -N {{ job_name }}
  # Number of nodes and MPI tasks per node:
  #$ -pe impi_hydra {{ 30 * n_nodes }}
  #$ -l h_rt={{ formatted_time }}

  module unload gromacs
  module load {{ module }}
  module load impi

  # Run gromacs/{{ version }} for {{ time - 5 }} minutes
  mpiexec -n {{ 30 * n_nodes }} -perhost 30 mdrun_mpi -v -maxh {{ time / 60 }} -deffnm {{ name }}

Slurm
-----

The following showcases the job template for the MPCDF cluster ``draco`` using
Slurm.

.. code::

  #!/bin/bash -l
  # Standard output and error:
  #SBATCH -o ./{{ job_name }}.out.%j
  #SBATCH -e ./{{ job_name }}.err.%j
  # Initial working directory:
  #SBATCH -D ./
  # Job Name:
  #SBATCH -J {{ job_name }}
  #
  # Queue (Partition):
  {%- if gpu %}
  #SBATCH --partition=gpu
  #SBATCH --constraint='gpu'
  {%- else %}
  {%- if time is lessthan 30 or time is equalto 30 %}
  #SBATCH --partition=express
  {%- elif time is greaterthan 30 and time is lessthan 240 or time is equalto 240 %}
  #SBATCH --partition=short
  {%- else %}
  #SBATCH --partition=general
  {%- endif %}
  {%- endif %}
  #
  # Number of nodes and MPI tasks per node:
  #SBATCH --nodes={{ n_nodes }}
  #SBATCH --ntasks-per-node=32
  # Wall clock limit:
  #SBATCH --time={{ formatted_time }}

  module purge
  module load impi
  module load cuda
  module load {{ module }}

  # Run {{ module }} for {{ time  }} minutes
  srun gmx_mpi mdrun -v -maxh {{ time / 60 }} -deffnm {{ name }}


LoadLeveler
-----------

Here is an example job template for the MPG cluster ``hydra`` (LoadLeveler).

.. code::

    # @ shell=/bin/bash
    #
    # @ error = {{ job_name }}.err.$(jobid)
    # @ output = {{ job_name }}.out.$(jobid)
    # @ job_type = parallel
    # @ node_usage = not_shared
    # @ node = {{ n_nodes }}
    # @ tasks_per_node = 20
    {%- if gpu %}
    # @ requirements = (Feature=="gpu")
    {%- endif %}
    # @ resources = ConsumableCpus(1)
    # @ network.MPI = sn_all,not_shared,us
    # @ wall_clock_limit = {{ formatted_time }}
    # @ queue

    module purge
    module load {{ module }}

    # run {{ module }} for {{ time }} minutes
    poe gmx_mpi mdrun -deffnm {{ name }} -maxh {{ time / 60 }}

Options passed to job templates
-------------------------------

MDBenchmark passes the following variables to each template:

+----------------+---------------------------------------------------------------------+
| Value          | Description                                                         |
+================+=====================================================================+
| name           | Name of the TPR file                                                |
+----------------+---------------------------------------------------------------------+
| job_name       | Job name as specified by the user, if not specified same as name    |
+----------------+---------------------------------------------------------------------+
| gpu            | Boolean that is true, if GPUs are requested                         |
+----------------+---------------------------------------------------------------------+
| module         | Name of the module to load                                          |
+----------------+---------------------------------------------------------------------+
| n_nodes        | Maximal number of nodes to run on                                   |
+----------------+---------------------------------------------------------------------+
| time           | Benchmark run time in minutes                                       |
+----------------+---------------------------------------------------------------------+
| formatted_time | Run time for the queuing system in human readable format (HH:MM:SS) |
+----------------+---------------------------------------------------------------------+

To ensure correct termination of jobs ``formatted_time`` is 5 minutes longer
than ``time``.

MDBenchmark will look for user templates in the `xdg`_ config folders defined by
the environment variables ``XDG_CONFIG_HOME`` and ``XDG_CONFIG_DIRS`` which by
default are set to ``$HOME/.config/MDBenchmark`` and ``/etc/xdg/MDBenchmark``,
respectively. If the variable ``MDBENCHMARK_TEMPLATES`` is set, the script will
also search in that directory.

MDBenchmark will first search in ``XDG_CONFIG_HOME`` and ``XDG_CONFIG_DIRS`` for
a suitable template file. This means it is possible to overwrite system-wide
installed templates or templates shipped with the package.

.. _xdg: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
