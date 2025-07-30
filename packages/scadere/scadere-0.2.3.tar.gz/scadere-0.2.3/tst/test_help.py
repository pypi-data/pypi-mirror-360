# Tests for CLI help formatting
# SPDX-FileCopyrightText: 2025 Nguyễn Gia Phong
# SPDX-License-Identifier: AGPL-3.0-or-later

from contextlib import redirect_stdout, suppress
from io import StringIO

from hypothesis import example, given
from pytest import fixture, mark, raises

from scadere import EXAMPLE_PREFIX, EXAMPLE_DESCRIPTION_PREFIX, NetLoc
from scadere.check import main as check
from scadere.listen import main as listen


@fixture(scope='session')
def help_string(request):
    string = StringIO()
    with suppress(SystemExit), redirect_stdout(string):
        request.param(arguments=['--help'])
    return string.getvalue()


@mark.parametrize('help_string', [check, listen], indirect=True)
def test_usage_prefix(help_string):
    assert help_string.startswith('Usage: ')


@mark.parametrize('help_string', [check, listen], indirect=True)
def test_options_heading(help_string):
    assert '\n\nOptions:\n' in help_string


@mark.parametrize('help_string', [check], indirect=True)
def test_one_or_more(help_string):
    assert ' HOST[:PORT]...\n' in help_string


@mark.parametrize('help_string', [check], indirect=True)
@mark.parametrize('short,long,metavar', [('-d', '--days', 'DAYS'),
                                         ('-o', '--output', 'PATH')])
def test_long_option(help_string, short, long, metavar):
    assert f'{short} {metavar}, {long}={metavar}' in help_string


@mark.parametrize('help_string', [check, listen], indirect=True)
def test_examples(help_string):
    epilog_index = help_string.find('\n\nExamples:\n')
    assert epilog_index >= 0
    epilog = help_string[epilog_index:].removeprefix('\n\n')
    examples = epilog[:epilog.find('\n\n')]
    lines = examples.removeprefix('Examples:\n').splitlines()

    assert EXAMPLE_DESCRIPTION_PREFIX.startswith(EXAMPLE_PREFIX)
    assert not lines[0].startswith(EXAMPLE_DESCRIPTION_PREFIX)
    assert lines[-1].startswith(EXAMPLE_DESCRIPTION_PREFIX)

    must_be_desc = False
    for line in lines:
        if must_be_desc:
            assert line.startswith(EXAMPLE_DESCRIPTION_PREFIX)
            must_be_desc = False
        else:
            assert line.startswith(EXAMPLE_PREFIX)
            must_be_desc = not line.startswith(EXAMPLE_DESCRIPTION_PREFIX)


@example('a.example:b', None)  # string is unlikely to match .*:\D+
@example('a.example:98', None)  # string is unlikely to match .*:\d+
@given(...)
def test_netloc(string: str, default_port: int | None):
    netloc = NetLoc(default_port)
    if ':' not in string:
        assert netloc(string) == (string, default_port)
    else:
        hostname, port = string.rsplit(':', 1)
        try:
            port_number = int(port)
        except ValueError:
            with raises(ValueError):
                netloc(string)
        else:
            assert netloc(string) == (hostname, port_number)
