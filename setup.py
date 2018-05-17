# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017 Max Linke & Michael Gecht and contributors
# (see the file AUTHORS for the full list of names)
#
# MDBenchmark is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MDBenchmark is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MDBenchmark.  If not, see <http://www.gnu.org/licenses/>.
import io
import os
import re

from setuptools import find_packages, setup


# modified from https://stackoverflow.com/a/41110107/2207958
def get_property(prop, project):
    with open(project + '/__init__.py') as fh:
        result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
                           fh.read())
    return result.group(1)


# Import the README and use it as the long-description.
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable', 'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: MacOS :: MacOS X', 'Operating System :: POSIX',
    'Programming Language :: Python', 'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6', 'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Chemistry',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: System :: Benchmark'
]

project_name = 'mdbenchmark'
setup(
    name=project_name,
    version=get_property('__version__', project_name),
    description='Benchmark molecular dynamics simulations',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/bio-phys/MDBenchmark',
    author='Max Linke, Michael Gecht',
    license='GPLv3',
    classifiers=CLASSIFIERS,
    keywords='benchmark molecular dynamics simulations gromacs namd',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.8',
        'mdsynthesis',
        'click',
        'jinja2',
        'pandas',
        'matplotlib',
        'python-Levenshtein',
        'xdg<2',
    ],
    package_data={'mdbenchmark': ['templates/*']},
    entry_points={'console_scripts': ['mdbenchmark=mdbenchmark.cli:cli']},
    tests_require=['pytest'],
    zip_safe=False)
