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
import click


class AliasedGroup(click.Group):
    aliases = {'submit': 'start'}

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        if cmd_name in self.aliases:
            return click.Group.get_command(self, ctx, self.aliases[cmd_name])
        ctx.fail('Sub commond unkown: {}'.format(cmd_name))

@click.command(cls=AliasedGroup)
@click.version_option()
def cli():
    """Generate and run benchmark jobs for GROMACS simulations"""
    pass
