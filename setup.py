# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# Benchmark
# Copyright (c) 2017 Max Linke & Michael Gecht and contributors
# (see the file AUTHORS for the full list of names)
#
# benchmark is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# benchmark is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with benchmark.  If not, see <http://www.gnu.org/licenses/>.import os
from setuptools import setup

setup(
    name='benchmark',
    version='3.0.0',
    description='benchmark gromacs simulations',
    author='Max Linke, Michael Gecht',
    license='GPL 3',
    packages=['benchmark'],
    package_data={'benchmark': ['templates/*']},
    install_requires=[
        'numpy>=1.8', 'mdsynthesis', 'click', 'jinja2', 'pandas', 'matplotlib',
        'python-Levenshtein', 'xdg',
    ],
    entry_points={'console_scripts': ['benchmark=benchmark.cli:cli']},
    zip_safe=False)
