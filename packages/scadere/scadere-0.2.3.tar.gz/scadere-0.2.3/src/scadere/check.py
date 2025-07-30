# TLS certificate expiration checker
# SPDX-FileCopyrightText: 2025 Nguyễn Gia Phong
# SPDX-License-Identifier: AGPL-3.0-or-later

from argparse import ArgumentParser, FileType
from base64 import urlsafe_b64encode as base64
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime as parsedate
from itertools import chain
from os.path import basename
from socket import AF_INET, socket
from ssl import create_default_context as tls_context
from sys import argv, stderr, stdout
from unicodedata import category as unicode_category
from uuid import uuid4

from . import GNUHelpFormatter, NetLoc, format_epilog, format_version

__all__ = ['main']


def is_control_character(character):
    """Check if a Unicode character belongs to the control category."""
    return unicode_category(character) == 'Cc'


def printable(string):
    """Check if the given Unicode string is printable."""
    return not any(map(is_control_character, string))


def base64_from_str(string):
    """Convert string to base64 format in bytes."""
    return base64(string.encode()).decode()


def check(netlocs, after, output, fake_ca=None):
    """Check if each netloc's TLS certificate expires after given time.

    Print the certificate's summary to output file if that is the case.
    """
    ctx = tls_context()
    if fake_ca is not None:  # for testing
        fake_ca.configure_trust(ctx)

    for hostname, port in netlocs:
        now = datetime.now(timezone.utc).isoformat()
        netloc = f'{hostname}:{port}'
        stderr.write(f'TLS certificate for {netloc} ')
        try:
            with ctx.wrap_socket(socket(AF_INET),
                                 server_hostname=hostname) as conn:
                conn.connect((hostname, port))
                cert = conn.getpeercert()
        except Exception as exception:
            stderr.write(f'cannot be retrieved: {exception}\n')
            print(now, 'N/A', hostname, port, uuid4().int,
                  base64_from_str(str(exception)), file=output)
            continue

        try:
            not_before = parsedate(cert['notBefore'])
            not_after = parsedate(cert['notAfter'])
            ca = dict(chain.from_iterable(cert['issuer']))['organizationName']
            if not printable(ca):
                raise ValueError(f'CA name contains control character: {ca!r}')
            serial = int(cert['serialNumber'], 16)
        except Exception as exception:
            stderr.write(f'cannot be parsed: {exception}\n')
            print(now, 'N/A', hostname, port, uuid4().int,
                  base64_from_str(str(exception)), file=output)
        else:
            if after < not_after:
                after_seconds = after.isoformat(timespec='seconds')
                stderr.write(f'will not expire at {after_seconds}\n')
            else:
                stderr.write(f'will expire at {not_after.isoformat()}\n')
                print(not_before.isoformat(), not_after.isoformat(),
                      # As unique identifier
                      hostname, port, serial,
                      base64_from_str(ca), file=output)


def main(prog=basename(argv[0]), arguments=argv[1:]):
    """Run TLS checker."""
    desc = ('Check TLS certificate expiration of HOST,'
            ' where PORT defaults to 443.\n\n'
            'The output is intended to be used by scadere-listen(1).')
    examples = [((f'{prog} --output=/var/lib/scadere/certificates'
                  ' example.com example.net'),
                 ('check if TLS certificates used by example.com:443'
                  ' and example.net:443 are either invalid'
                  ' or expiring within the next week,'
                  ' then write the result to /var/lib/scadere/certificates.'))]

    parser = ArgumentParser(prog=prog, allow_abbrev=False, description=desc,
                            epilog=format_epilog(examples),
                            formatter_class=GNUHelpFormatter)
    parser.add_argument('-v', '--version', action='version',
                        version=format_version('scadere-check',
                                               '2025', 'Nguyễn Gia Phong'))
    parser.add_argument('netloc', metavar='HOST[:PORT]',
                        nargs='+', type=NetLoc(443))
    parser.add_argument('-d', '--days', type=float, default=7,
                        help='days before expiration (default to 7)')
    parser.add_argument('-o', '--output', metavar='PATH',
                        type=FileType('w'), default=stdout,
                        help='output file (default to stdout)')

    args = parser.parse_args(arguments)
    with args.output:  # pragma: no cover
        after = datetime.now(timezone.utc) + timedelta(days=args.days)
        check(args.netloc, after, args.output)


if __name__ == '__main__':  # pragma: no cover
    main()
