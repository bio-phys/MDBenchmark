=================
 Install package
=================

Install in develop mode to notice changes immediately.

.. code::

   python setup.py develop

==================
  Doing a Release
==================

Updating CHANGELOG
------------------

Install and run towncrier in the project directory.

.. code::

   towncrier

If towncrier doesn't delete item in the *changelog* folder remove them by hand.

Generate dist files
-------------------

This is from the python tutorial_.

We can generate a source distribution package

.. code::

   python setup.py sdist

We will also build wheels. Since we are pure python a universal wheel is possible

.. code::

   pip install --upgrade wheel
   python setup.py bdist_wheel --universal

Check that the source tarball in *dist* contains all important files!

Publish on Github
-----------------

mark tag on github an release

Publish to PyPi
---------------
upload with twine

.. code::

   twine upload dist/*

Publish to Conda-Forge
----------------------

After the pypi upload update the conda-forge recipe


.. _tutorial: https://packaging.python.org/tutorials/distributing-packages/
