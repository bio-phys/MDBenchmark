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
from setuptools import setup
import re

# modified from https://stackoverflow.com/a/41110107/2207958
def get_property(prop, project):
    with open(project + '/__init__.py') as fh:
        result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), fh.read())
    return result.group(1)

project_name = 'mdbenchmark'
setup(
    name=project_name,
    version=get_property('__version__', project_name),
    description='mdbenchmark gromacs simulations',
    author='Max Linke, Michael Gecht',
    license='GPL 3',
    packages=['mdbenchmark'],
    package_data={'mdbenchmark': ['templates/*']},
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
    entry_points={'console_scripts': ['mdbenchmark=mdbenchmark.cli:cli']},
    tests_require=['pytest'],
    zip_safe=False)
