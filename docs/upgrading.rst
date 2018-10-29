Upgrading
=========

While we try to make upgrades from one version of MDBenchmark to another as easy
as possible, we are sometimes forced to break things along the way. This page
gives some guidelines on how to migrate to specific versions of MDBenchmark, if
you have been using a different version before.

Upgrading from version
----------------------

Version 2.0.0
~~~~~~~~~~~~~

.. note::

  **TL;DR:**
  You need to uninstall the unneeded ``datreant.core``, ``datreant.data`` and ``mdsynthesis`` Python packages. Or just get rid of the current environment, e.g., ``conda env remove -n benchmark`` if you are using ``conda``, and :ref:`create it from scratch <conda-install>`.

Starting from version 2.0.0, MDBenchmark migrated to a different dependency,
than it used before. While the specialized |mdsynthesis|_ package was used in
previous version, we migrated to the more general |datreant|_ package. This
leads to two things:

1) Previously, every folder representing a specific number of nodes contained a
   ``Sim.<uuid>.json`` file, where ``<uuid>`` is a `UUID`_. This file contained
   all information representing a specific benchmark with its parameters. With
   the newer version of ``datreant``, the format was changed and now each of
   these folders contains a ``.datreant`` folder instead.

2) ``datreant`` version 1.0 changed its package layout and led to the necessity
   of uninstalling previous packages. Because we were using a previous
   ``datreant`` version, you as a user will also need to uninstall those
   packages.

Uninstalling old packages
#########################

For proper migration, you need to uninstall the following three packages:

1) ``datreant.core``
2) ``datreant.data``
3) ``mdsynthesis``

If you are using ``conda`` and your environment is called ``benchmark``, run the
following command::

  conda remove -n benchmark datreant.core datreant.data mdsynthesis

You can also decide to fully remove the environment (``conda env remove -n
benchamrk``) and :ref:`create it from scratch <conda-install>`.

If you are using ``pip`` simply run::

  pip uninstall datreant.core datreant.data mdsynthesis

.. |mdsynthesis| replace:: ``mdsynthesis``
.. _mdsynthesis: https://mdsynthesis.readthedocs.io/en/master/
.. |datreant| replace:: ``datreant``
.. _datreant: https://datreant.readthedocs.io/en/master/
.. _UUID: https://en.wikipedia.org/wiki/Universally_unique_identifier
