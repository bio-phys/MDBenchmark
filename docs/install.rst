Installation
============

Why isolated environments matter
--------------------------------

Installing a new python package into the main python environment of your system
can lead to unforeseen consequences. Python packages can have dependencies on
different versions of the same package, i.e. ``numpy``. If package ``packageA``
depends on ``numpy==1.14.1`` and you install ``packageB``, which depends on
``numpy==1.9.2``, then ``packageA`` may stop to work. Isolating packages into
their own environments makes sure to provide the needed dependencies, while not
disrupting the dependencies of other packages (in other environments).

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

    conda create -n benchmark
    conda install -n benchmark -c conda-forge mdbenchmark

Before every usage of ``mdbenchmark``, you need to first activate the conda
environment via ``source activate benchmark``. After doing this once, you can
use ``mdbenchmark`` for the duration of your shell session.

.. code::

   source activate benchmark

Install via ``pip``
-------------------

Installation with ``pip`` should also be done inside a virtual environment.

.. code::

   python3 -m venv benchmark-env

This created a new directory called ``benchmark-env``, if it did not exist
before. Now you can activate the environment, as described above.

.. code::

   source benchmark-env/bin/activate

After activating the environment, you should be able to install the package via
``pip``. **Note:** the ``--user`` option leads to the installation of the
package in your ``$HOME`` directory. If you are not using the option, you may
get errors due to missing write permissions.

.. code::

   pip install --user mdbenchmark

The biggest downside is, that you need to remember where you put the virtual
environment and always specify the path when activating. It's somewhat easier
with ``conda``. Several python packages try to make up for this and provide some
wrappers, like `virtualenvwrapper`_.


Install via ``pipenv``
----------------------

The easiest way is to install the package via ``pipenv``. First install
``pipenv`` (refer to `documentation`_).

.. code::

   pip install --user pipenv

Now you can let ``pipenv`` take care of creating the virtual environment. The
one downside here is, that you will always need to call ``mdbenchmark`` from the
folder you installed it in.

.. code::

   pipenv install mdbenchmark
   pipenv run mdbenchmark

.. _virtual environment: https://docs.python.org/3/tutorial/venv.html
.. _conda environment: https://conda.io/docs/user-guide/tasks/manage-environments.html
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _documentation: https://docs.pipenv.org/install/#pragmatic-installation-of-pipenv
