# Root package, with some helpers
# SPDX-FileCopyrightText: 2025 Nguyễn Gia Phong
# SPDX-License-Identifier: AGPL-3.0-or-later

from argparse import HelpFormatter, ONE_OR_MORE
from functools import cache
from importlib.resources import files

__all__ = ['__version__', 'GNUHelpFormatter', 'NetLoc',
           'atom2xhtml', 'format_epilog', 'format_version']
__version__ = '0.2.3'

EXAMPLE_PREFIX = ' ' * 2
# help2man's implementation detail
EXAMPLE_DESCRIPTION_PREFIX = ' ' * 20


class GNUHelpFormatter(HelpFormatter):
    """Help formatter for ArgumentParser following GNU Coding Standards."""

    def add_usage(self, usage, actions, groups, prefix='Usage: '):
        """Substitute 'Usage:' for 'usage:'."""
        super().add_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        """Substitute 'Options:' for 'options:'."""
        super().start_section(heading.capitalize())

    def _fill_text(self, text, width, indent):
        """Preserve examples' formatting."""
        desc_position = max(len(EXAMPLE_DESCRIPTION_PREFIX),
                            min(self._action_max_length+2,
                                self._max_help_position))
        desc_width = width - desc_position
        desc_indent = indent + ' '*desc_position
        example_indent = indent + EXAMPLE_PREFIX
        parts = []
        for line in text.splitlines():
            if line.startswith(EXAMPLE_DESCRIPTION_PREFIX):
                parts.append(super()._fill_text(line, desc_width, desc_indent))
            elif line.startswith(EXAMPLE_PREFIX):
                parts.append(example_indent+line.strip())
            else:  # not example
                parts.append(super()._fill_text(line, width, indent))
        return '\n'.join(parts)

    def _format_args(self, action, default_metavar):
        """Substitute 'METAVAR...' for 'METAVAR [METAVAR ...]'."""
        if action.nargs == ONE_OR_MORE:
            get_metavar = self._metavar_formatter(action, default_metavar)
            return '{}...'.format(*get_metavar(1))
        return super()._format_args(action, default_metavar)

    def _format_action_invocation(self, action):
        """Format --long-option=argument."""
        if not action.option_strings or action.nargs is not None:
            return super()._format_action_invocation(action)
        arg = self._format_args(action,
                                self._get_default_metavar_for_optional(action))
        return ', '.join(f"{opt}{'=' if opt.startswith('--') else ' '}{arg}"
                         for opt in action.option_strings)

    def add_argument(self, action):
        """Suppress positional arguments."""
        if action.option_strings:
            super().add_argument(action)


class NetLoc:
    """Network location with default port."""

    def __init__(self, default_port):
        self.default_port = default_port

    def __call__(self, string):
        """Return hostname and port from given netloc."""
        if ':' not in string:
            return string, self.default_port
        hostname, port = string.rsplit(':', 1)
        return hostname, int(port)  # ValueError to be handled by argparse


@cache
def atom2xhtml():
    """Load stylesheet from package resources exactly once."""
    return files(__name__).joinpath('atom2xhtml.xslt').read_bytes()


def format_epilog(examples):
    """Format example commands and their description ."""
    lines = ['Examples:']
    for example, description in examples:
        lines.append(EXAMPLE_PREFIX+example)
        lines.append(EXAMPLE_DESCRIPTION_PREFIX+description)
    lines.append('\nReport bugs to <chung@loa.loang.net>.')
    return '\n'.join(lines)


def format_version(prog, copyright_years, authors):
    """Format version information."""
    return (f'{prog} {__version__}\n\n'
            f'Copyright (C) {copyright_years} {authors}.\n\n'
            'This is free software: you are can redistribute and/or modify it'
            ' under the terms of the GNU Affero General Public License'
            ' version 3 or later <https://gnu.org/licenses/agpl>.\n\n'
            'There is NO WARRANTY, to the extent permitted by law.\n\n'
            f'Written by {authors}.')
