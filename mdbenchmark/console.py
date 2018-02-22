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
import sys

import click
import six


def console_wrapper(message,
                    prefix=None,
                    filehandler=None,
                    args=None,
                    bold=True,
                    fg=None,
                    bg=None,
                    underline=None,
                    blink=None,
                    **kwargs):
    """Wrapper to consolidate all click.echo() calls.

    Parameters
    ----------
    message : str
        Message to print to the console.
    prefix : str
        String that prefixes the message.
    filehandler : StringIO
        Redirect the `click.echo` output to `filehandler`. Only used internally.
    args
        List of strings passed into `.format` to replace placeholders in `message`.
    bold : bool
        Passed to `click.style` to make placeholders bold.
    fg : bool
        Passed to `click.style` to change text color of placeholders.
    bg : bool
        Passed to `click.style` to change background color of placeholders.
    underline : bool
        Passed to `click.style` to underline text of placeholders.
    blink : bool
        Passed to `click.style` to make placeholders blink.
    **kwargs
        Keyword arguments passed into `.format` to replace named placeholders in `message`.

    Raises
    ------
    ValueError
        If the number of placeholders and arguments is not the same,
        or if passed incorrect named arguments.
    """
    if args is None:
        args = []

    if prefix is not None:
        message = '{} {}'.format(prefix, message)

    if args:
        args = [
            click.style(
                str(arg),
                bold=bold,
                fg=fg,
                bg=bg,
                underline=underline,
                blink=blink) for arg in args
        ]

    if kwargs:
        kwargs = {
            k: click.style(
                str(v), bold=bold, fg=fg, bg=bg, underline=underline)
            for k, v in six.iteritems(kwargs)
        }

    try:
        click.echo(message.format(*args, **kwargs), file=filehandler)
    except IndexError:
        raise ValueError(
            'Number of placeholders do not correspond to the number of curly brackets '
            'inside the string.')


def info(message, *args, **kwargs):
    """Output the message without any further formatting."""
    console_wrapper(message, args=args, **kwargs)


def warn(message, *args, **kwargs):
    """Output a warning to the users console."""
    prefix = click.style('WARNING', fg='yellow', bold=True)

    console_wrapper(message, prefix=prefix, args=args, **kwargs)


def error(message, *args, **kwargs):
    """Output an error to the users console and stop execution of the script."""
    prefix = click.style('ERROR', fg='red', bold=True)

    console_wrapper(message=message, prefix=prefix, args=args, **kwargs)
    sys.exit(1)
