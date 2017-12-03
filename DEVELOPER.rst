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


Publish to PyPi
---------------

This is from the python tutorial_.

We can generate a source distribution package

.. code::

   python setup.py sdist

We will also build wheels. Since we are pure python a universal wheel is possible

.. code::

   pip install --upgrade wheel
   python setup.py bdist_wheel --universal


upload with twine


.. code::

   twine upload dist/*


.. _tutorial: https://packaging.python.org/tutorials/distributing-packages/
