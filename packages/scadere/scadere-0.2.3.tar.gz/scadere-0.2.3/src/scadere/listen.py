# HTTP server for Atom feed of TLS certificate expirations
# SPDX-FileCopyrightText: 2025 Nguyễn Gia Phong
# SPDX-License-Identifier: AGPL-3.0-or-later

from argparse import ArgumentParser
from asyncio import run, start_server
from base64 import urlsafe_b64decode as from_base64
from datetime import datetime, timezone
from functools import lru_cache, partial
from http import HTTPStatus
from locale import LC_TIME, setlocale
from operator import call
from os.path import basename
from pathlib import Path
from string import digits
from sys import argv
from typing import assert_never
from urllib.parse import parse_qs, urljoin, urlsplit
from xml.etree.ElementTree import (Element as xml_element,
                                   SubElement as xml_subelement,
                                   indent, tostring as string_from_xml)

from . import (__version__, GNUHelpFormatter, NetLoc,
               atom2xhtml, format_epilog, format_version)
from .check import base64_from_str

__all__ = ['main']


@lru_cache
def read_text(file, time):
    """Read the given text file if it has been updated."""
    return file.read_text()


def datetime_from_str(string, unavailable_ok=False):
    """Parse datetime from string in ISO 8601 format."""
    if string == 'N/A' and unavailable_ok:
        return None
    return datetime.fromisoformat(string).astimezone(timezone.utc)


def str_from_base64(string64):
    """Decode string in base64 format."""
    return from_base64(string64.encode()).decode()


def parse_summary(line):
    """Parse TLS certificate into a summary tuple."""
    return tuple(map(call,
                     (datetime_from_str,
                      partial(datetime_from_str, unavailable_ok=True),
                      str, int, int, str_from_base64),
                     line.rstrip('\r\n').split(' ', maxsplit=5)))


def path(hostname, port, number, string):
    """Return the relative URL for the given certificate's details."""
    return f'{hostname}/{port}/{base64_from_str(string)}/{number}'


def supported_http_version(version):
    """Check if given HTTP version complies with section 2.5 of RFC 9110."""
    match len(version):
        case 1:
            return version in digits
        case 3:
            major, period, minor = version
            return major in digits and period == '.' and minor in digits
        case _:
            return False


def write_status(writer, http_version, status):
    """Write the given HTTP status line."""
    status = f'HTTP/{http_version} {status.value} {status.phrase}\r\n'
    writer.write(status.encode())


def write_content_type(writer, content_type):
    """Write the given HTTP content type."""
    writer.write(f'Content-Type: {content_type}\r\n'.encode())


def describe_status(writer, status, http_version='1.1'):
    """Write a HTTP/1.1 response including status description."""
    write_status(writer, http_version, status)
    content = f'{status.description}\n'.encode()
    write_content_type(writer, 'text/plain')
    writer.write(f'Content-Length: {len(content)}\r\n\r\n'.encode())
    writer.write(content)


def body(not_before, not_after, hostname, port, number, string):
    """Describe the given certificate in XHTML."""
    if not_after is None:
        return (('h1', 'TLS certificate problem'),
                ('dl',
                 ('dt', 'Domain'), ('dd', hostname),
                 ('dt', 'Port'), ('dd', port),
                 ('dt', 'Time'), ('dd', not_before),
                 ('dt', 'Error'), ('dd', string)))
    return (('h1', 'TLS certificate information'),
            ('dl',
             ('dt', 'Domain'), ('dd', hostname),
             ('dt', 'Port'), ('dd', port),
             ('dt', 'Issuer'), ('dd', string),
             ('dt', 'Serial number'), ('dd', number),
             ('dt', 'Valid from'), ('dd', not_before),
             ('dt', 'Valid until'), ('dd', not_after)))


def entry(base_url, cert):
    """Construct Atom entry for the given TLS certificate."""
    not_before, not_after, hostname, port, number, string = cert
    url = urljoin(base_url, path(hostname, port, number, string))
    title = (f'TLS cert for {hostname} cannot be retrieved'
             if not_after is None
             else f'TLS cert for {hostname} will expire at {not_after}')
    author = 'Scadere' if not_after is None else string
    return ('entry',
            ('author', ('name', author)),
            ('content', {'type': 'xhtml'},
             ('div', {'xmlns': 'http://www.w3.org/1999/xhtml'}, *body(*cert))),
            ('id', url),
            ('link', {'rel': 'alternate',
                      'type': 'application/xhtml+xml',
                      'href': url}),
            ('title', title),
            ('updated', not_before))


def split_domain(domain):
    """Split domain and order by ascending level."""
    return tuple(domain.split('.')[::-1])


def is_subdomain(subject, objects):
    """Check if subject is a subdomain of any object."""
    if not objects:
        return True
    sbj_parts = split_domain(subject)
    return any(sbj_parts[:len(obj_parts)] == obj_parts
               for obj_parts in map(split_domain, objects))


def feed(base_url, query, name, mtime, certificates):
    """Construct an Atom feed based on the given information."""
    url = f'{base_url}?{query}'
    domains = tuple(parse_qs(query).get('domain', []))
    return ('feed', {'xmlns': 'http://www.w3.org/2005/Atom'},
            ('id', url),
            ('link', {'rel': 'self', 'href': url}),
            ('title', name),
            ('updated', mtime),
            ('generator',
             {'uri': 'https://trong.loang.net/scadere/about',
              'version': __version__},
             'Scadere'),
            *(entry(base_url, cert) for cert in certificates
              if is_subdomain(cert[2], domains)))


def page(not_before, not_after, hostname, port, *args):
    """Construct an XHTML page for the given TLS certificate."""
    return ('html', {'xmlns': 'http://www.w3.org/1999/xhtml',
                     'lang': 'en'},
            ('head',
             ('meta', {'name': 'color-scheme',
                       'content': 'dark light'}),
             ('meta', {'name': 'viewport',
                       'content': ('width=device-width,'
                                   'initial-scale=1.0')}),
             ('link', {'rel': 'icon', 'href': 'data:,'}),
             ('title', f'TLS certificate - {hostname}:{port}')),
            ('body', *body(not_before, not_after, hostname, port, *args)))


def xml(tree, parent=None):
    """Construct XML element from the given tree."""
    tag, attrs, children = ((tree[0], tree[1], tree[2:])
                            if isinstance(tree[1], dict)
                            else (tree[0], {}, tree[1:]))
    if parent is None:
        elem = xml_element(tag, attrs)
    else:
        elem = xml_subelement(parent, tag, attrs)
    for child in children:
        match child:
            case tuple():
                xml(child, elem)
            case str():
                elem.text = child
            case int():
                elem.text = str(child)
            case datetime():
                elem.text = child.isoformat()
            case _:
                assert_never(child)
    if parent is None:
        indent(elem)
    return elem


@lru_cache
def atom2xhtml_url(base_url):
    """Return the URL to the immutable stylesheet."""
    return urljoin(base_url, f'{urlsplit(base_url).path}{__version__}.xslt')


@lru_cache
def unparsed_feed(base_url, *args):
    """Cache Atom feed."""
    return (b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<?xml-stylesheet type="text/xsl"'
            + f' href="{atom2xhtml_url(base_url)}"?>\n'.encode()
            + string_from_xml(xml(feed(base_url, *args)), 'utf-8'))


@lru_cache
def unparsed_page(*args):
    """Cache XHTML page."""
    return string_from_xml(xml(page(*args)), 'utf-8', xml_declaration=True)


@lru_cache
def set_http_time_locale():
    """Set LC_TIME=C exactly once."""
    setlocale(LC_TIME, 'C')


def write_xml(writer, http_version, subtype, func, *args, mtime=None):
    """Write given document as XML."""
    try:
        content = func(*args)
    except Exception:  # pragma: no cover
        describe_status(writer, HTTPStatus.INTERNAL_SERVER_ERROR, http_version)
        raise
    else:
        write_status(writer, http_version, HTTPStatus.OK)
        if subtype == 'atom':
            # Firefox would try to download an application/atom+xml
            # and Chromium would display its source code
            # instead of applying the XSLT stylesheet
            # and rendering the resulting hypertext.
            write_content_type(writer, 'application/xml')
        else:
            write_content_type(writer, f'application/{subtype}+xml')
        writer.write(f'Content-Length: {len(content)}\r\n'.encode())
        if mtime is None:
            writer.write(b'Cache-Control: public,'
                         b' max-age: 31536000, immutable\r\n\r\n')
        else:
            set_http_time_locale()
            http_time = mtime.strftime('%a, %d %b %Y %H:%M:%S GMT')
            writer.write(f'Last-Modified: {http_time}\r\n\r\n'.encode())
        writer.write(content)


async def handle(certs, base_url, reader, writer, title=''):
    """Handle HTTP request."""
    try:
        try:
            request = await reader.readuntil(b'\r\n')
        except Exception:
            describe_status(writer, HTTPStatus.BAD_REQUEST)
            return

        if not request.startswith(b'GET '):
            describe_status(writer, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        try:
            # Raise ValueError on the lack of b'HTTP/'
            url, version = request.removeprefix(b'GET ').rsplit(b' HTTP/', 1)
            http_version = version.strip().decode()
            if not supported_http_version(http_version):
                raise ValueError
        except ValueError:
            describe_status(writer, HTTPStatus.HTTP_VERSION_NOT_SUPPORTED)
            return

        try:
            mtime = datetime.fromtimestamp(certs.stat().st_mtime, timezone.utc)
            summaries = tuple(map(parse_summary,
                                  read_text(certs, mtime).splitlines()))
            paths = tuple(urlsplit(urljoin(base_url, path(*s[-4:]))).path
                          for s in summaries)
            lookup = dict(map(tuple, zip(paths, summaries)))
            assert len(lookup) == len(summaries)
            url_parts = urlsplit(urljoin(base_url, url.strip().decode()))
        except Exception:  # pragma: no cover
            describe_status(writer, HTTPStatus.INTERNAL_SERVER_ERROR,
                            http_version)
            raise

        if url_parts.path == urlsplit(base_url).path:  # Atom feed
            write_xml(writer, http_version, 'atom', unparsed_feed,
                      base_url, url_parts.query, title or certs.name,
                      mtime, summaries, mtime=mtime)
        elif url_parts.path == urlsplit(atom2xhtml_url(base_url)).path:
            write_xml(writer, http_version, 'xslt', atom2xhtml)
        elif url_parts.path in lookup:  # accessible Atom entry's link/ID
            write_xml(writer, http_version, 'xhtml', unparsed_page,
                      *lookup.get(url_parts.path))
        else:
            describe_status(writer, HTTPStatus.NOT_FOUND, http_version)
    finally:
        assert writer.can_write_eof()
        writer.write_eof()
        writer.close()
        await writer.wait_closed()


async def listen(certs, title, base_url, host, port):  # pragma: no cover
    """Serve HTTP server for TLS certificate expirations' Atom feed."""
    server = await start_server(partial(handle, certs, base_url, title=title),
                                host, port)
    async with server:
        print('Serving on', end=' ')
        print(*(socket.getsockname() for socket in server.sockets), sep=', ')
        await server.serve_forever()


def with_trailing_slash(base_url):
    """Return the base URL with a trailing slash."""
    return base_url if base_url.endswith('/') else f'{base_url}/'


def main(prog=basename(argv[0]), arguments=argv[1:]):
    """Launch server."""
    desc = ('Serve at URL Atom feeds for TLS certificate renewal reminder.'
            '  It is possible for clients to filter domains'
            ' using one or more "domain" URL queries.\n\n'
            'The certificate information is read from the file at PATH,'
            ' which is generated by scadere-check(1).\n\n'
            'The server listens for TCP connections coming to HOST:PORT,'
            ' where HOST defaults to localhost'
            ' and PORT is selected randomly if not specified.\n\n')
    examples = [((f'{prog} /var/lib/scadere/certificates'
                  ' https://scadere.example/ :4433'),
                 ('serve renewal reminder feed using information'
                  ' from /var/lib/scadere/certificates on localhost:4433,'
                  ' to be reverse proxied to https://scadere.example/')),
                ('https://scadere.example/',
                 'feed for all checked TLS certificates'),
                ('https://scadere.example/?domain=example.com&domain=net',
                 ('feed for checked TLS certificates for example.com,'
                  ' its subdomains, and domains under the TLD NET'))]

    parser = ArgumentParser(prog=prog, allow_abbrev=False, description=desc,
                            epilog=format_epilog(examples),
                            formatter_class=GNUHelpFormatter)
    parser.add_argument('-v', '--version', action='version',
                        version=format_version('scadere-listen',
                                               '2025', 'Nguyễn Gia Phong'))
    parser.add_argument('-t', '--title', default='',
                        help=('title of Atom feeds'
                              " (default to PATH's filename)"))
    parser.add_argument('certs', metavar='PATH', type=Path)
    parser.add_argument('base_url', metavar='URL', type=with_trailing_slash)
    parser.add_argument('netloc', metavar='[HOST][:PORT]', nargs='?',
                        type=NetLoc(None), default=('localhost', None))

    args = parser.parse_args(arguments)
    run(listen(args.certs, args.title,
               args.base_url, *args.netloc))  # pragma: no cover


if __name__ == '__main__':  # pragma: no cover
    main()
