# Tests for the HTTP server
# SPDX-FileCopyrightText: 2025 Nguyễn Gia Phong
# SPDX-License-Identifier: AGPL-3.0-or-later

from asyncio import open_unix_connection, start_unix_server
from contextlib import asynccontextmanager, contextmanager
from copy import deepcopy
from datetime import datetime, timezone
from email.parser import BytesHeaderParser
from functools import partial
from http import HTTPMethod
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp, mkstemp
from urllib.parse import urljoin, urlsplit
from xml.etree.ElementTree import (XML, XMLParser, indent,
                                   tostring as str_from_xml)

from hypothesis import HealthCheck, example, given, settings
from hypothesis.strategies import (booleans, composite, data,
                                   datetimes, from_type, integers, just,
                                   sampled_from, sets, text, uuids)
from hypothesis.provisional import domains, urls
from pytest import raises

from scadere import __version__, atom2xhtml
from scadere.check import base64_from_str, printable
from scadere.listen import (handle, is_subdomain, path, parse_summary,
                            str_from_base64, with_trailing_slash, xml)

ATOM_NAMESPACES = {'': 'http://www.w3.org/2005/Atom'}
XHTML_NAMESPACES = {'': 'http://www.w3.org/1999/xhtml'}
UTC_DATETIMES = datetimes(timezones=just(timezone.utc))


def ports():
    """Return a Hypothesis strategy for TCP ports."""
    return integers(1, 65535)


def serials():
    """Return a Hypothesis strategy for TLS serial number."""
    return integers(1, 256**20-1)


def base64s():
    """Return a Hypothesis strategy for printable strings in base64."""
    return text().filter(printable).map(base64_from_str)


@given(domains(), ports(), serials(), text())
def test_path(hostname, port, number, string):
    r = path(hostname, port, number, string).split('/')
    assert r[0] == hostname
    assert int(r[1]) == port
    assert int(r[3]) == number
    assert str_from_base64(r[2]) == string


@example('example.net', {'net'})
@given(domains(), sets(domains()))
def test_is_subdomain(subject, objects):
    if not objects:
        assert is_subdomain(subject, objects)
    elif is_subdomain(subject, objects):
        assert any(child == '' or child.endswith('.')
                   for child in map(subject.removesuffix, objects))
    else:
        for obj in objects:
            assert (not subject.endswith(obj)
                    or not subject.removesuffix(obj).endswith('.'))


def xml_unsupported_type(child):
    """Check if child is of a type supported by the XML constructor."""
    return not isinstance(child, (tuple, str, int, datetime))


@given(text(), from_type(type).flatmap(from_type).filter(xml_unsupported_type))
def test_xml_unsupported_type(tag, child):
    with raises(AssertionError, match='Expected code to be unreachable'):
        xml((tag, {}, child))


@composite
def certificates(draw):
    """Return a Hypothesis strategy for certificate summaries."""
    valid = draw(booleans())
    not_before = draw(UTC_DATETIMES).isoformat()
    not_after = draw(UTC_DATETIMES).isoformat() if valid else 'N/A'
    hostname = draw(domains())
    port = draw(ports())
    number = draw(serials()) if valid else draw(uuids(version=4)).int
    string = draw(base64s())
    return f'{not_before} {not_after} {hostname} {port} {number} {string}'


@contextmanager
def tmp_cert_file(lines):
    cert_file = Path(mkstemp(text=True)[1])
    cert_file.write_text('\n'.join(lines))
    try:
        yield cert_file
    finally:
        cert_file.unlink()


def is_base_url(url):
    """Check if the given URL has a trailing slash.

    The parser for command-line arguments
    enforces this property for base URLs.
    """
    return url.endswith('/')


@given(urls())
def test_with_trailing_slash(url):
    if is_base_url(url):
        assert with_trailing_slash(url) == url
    else:
        assert with_trailing_slash(url) == f'{url}/'


def is_root(base_url, url):
    """Check if the given URL points to the same base URL.

    Paths starting with // are excluded because urljoin
    sometimes confuse them with URL scheme.
    """
    base_path = urlsplit(base_url).path
    url_path = urlsplit(url).path
    return urlsplit(urljoin(base_url, url_path)).path == base_path


def has_usual_path(url):
    """Check if the given URL path tends to mess with urljoin."""
    return is_root(url, url)


@asynccontextmanager
async def connect(socket):
    """Return a read-write stream for an asyncio TCP connection."""
    reader, writer = await open_unix_connection(socket)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


async def write_request(writer, request):
    """Write given request."""
    writer.write(request.encode())
    await writer.drain()
    assert writer.can_write_eof()
    writer.write_eof()


async def fetch_xml(socket, url, content_type):
    """Fetch the content at the URL from the socket."""
    header_parser = BytesHeaderParser()
    xml_parser = XMLParser(encoding='utf-8')
    async with connect(socket) as (reader, writer):
        await write_request(writer, f'GET {url} HTTP/1.1\r\n')
        status = await reader.readuntil(b'\r\n')
        assert status == b'HTTP/1.1 200 OK\r\n'
        headers_bytes = await reader.readuntil(b'\r\n\r\n')
        headers = header_parser.parsebytes(headers_bytes)
        assert headers['Content-Type'] == content_type
        content = await reader.read()
        assert len(content) == int(headers['Content-Length'])
        return XML(content.decode(), xml_parser)


async def check_atom2xhtml(socket, url):
    """Check if socket serves atom2xhtml stylesheet at given HTTP URL."""
    header_parser = BytesHeaderParser()
    async with connect(socket) as (reader, writer):
        await write_request(writer, f'GET {url} HTTP/1.1\r\n')
        status = await reader.readuntil(b'\r\n')
        assert status == b'HTTP/1.1 200 OK\r\n'
        headers_bytes = await reader.readuntil(b'\r\n\r\n')
        headers = header_parser.parsebytes(headers_bytes)
        assert headers['Content-Type'] == 'application/xslt+xml'
        content = await reader.read()
        assert len(content) == int(headers['Content-Length'])
        assert content == atom2xhtml()


def equal_xml(a, b):
    """Check if the two XML elements are equal."""
    a_copy, b_copy = deepcopy(a), deepcopy(b)
    indent(a_copy)
    indent(b_copy)
    return str_from_xml(a_copy).rstrip() == str_from_xml(b_copy).rstrip()


async def check_feed(socket, base_url):
    """Check the Atom feed, its stylesheet, and entry pages."""
    feed = await fetch_xml(socket, base_url, 'application/xml')
    await check_atom2xhtml(socket, f'{base_url}{__version__}.xslt')
    for entry in feed.findall('entry', ATOM_NAMESPACES):
        link = entry.find('link', ATOM_NAMESPACES).attrib
        assert link['rel'] == 'alternate'
        page = await fetch_xml(socket, link['href'], link['type'])
        assert equal_xml(entry.find('.//dl', XHTML_NAMESPACES),
                         page.find('.//dl', XHTML_NAMESPACES))


async def check_server(handler, func, *args):
    """Test request handler using func."""
    d = Path(mkdtemp())
    socket = d / 'sock'
    try:
        async with await start_unix_server(handler, socket):
            await func(socket, *args)
    finally:
        rmtree(d)


def unique_netlocs(summaries):
    """Return summaries for unique network locations."""
    return {parse_summary(summary)[2:4]: summary
            for summary in summaries}.values()


@given(urls().filter(is_base_url).filter(has_usual_path),
       sets(certificates(), min_size=1).map(unique_netlocs),
       text().filter(printable))
@settings(suppress_health_check=(HealthCheck.filter_too_much,
                                 HealthCheck.too_slow))
async def test_content(base_url, certs, title):
    base_path = urlsplit(base_url).path
    with tmp_cert_file(certs) as cert_file:
        handler = partial(handle, cert_file, base_url, title=title)
        await check_server(handler, check_feed, base_path)


async def bad_request(socket, request):
    """Expect from socket a HTTP response with status 400."""
    async with connect(socket) as (reader, writer):
        await write_request(writer, request)
        status = await reader.readuntil(b'\r\n')
        assert status == b'HTTP/1.1 400 Bad Request\r\n'


@given(text().filter(lambda request: '\r\n' not in request))
async def test_incomplete_request(request):
    with tmp_cert_file(()) as cert_file:
        handler = partial(handle, cert_file, 'http://localhost')
        await check_server(handler, bad_request, request)


async def not_found(socket, url):
    """Send GET request for URL and expect HTTP status 404 from socket."""
    async with connect(socket) as (reader, writer):
        await write_request(writer, f'GET {url} HTTP/1\r\n')
        status = await reader.readuntil(b'\r\n')
        assert status == b'HTTP/1 404 Not Found\r\n'


@given(data())
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_unrecognized_url(drawer):
    base_url = drawer.draw(urls().filter(is_base_url), label='base URL')
    url = drawer.draw(urls().filter(lambda url: not is_root(base_url, url)),
                      label='request URL')
    with tmp_cert_file(()) as cert_file:
        handler = partial(handle, cert_file, base_url)
        await check_server(handler, not_found, urlsplit(url).path)


async def method_not_allowed(socket, method, url):
    """Expect from socket a HTTP response with status 405."""
    async with connect(socket) as (reader, writer):
        await write_request(writer, f'{method} {url} HTTP/1.1\r\n')
        status = await reader.readuntil(b'\r\n')
        assert status == b'HTTP/1.1 405 Method Not Allowed\r\n'


@given(urls(), sampled_from(HTTPMethod).filter(lambda method: method != 'GET'))
async def test_unallowed_method(base_url, method):
    with tmp_cert_file(()) as cert_file:
        handler = partial(handle, cert_file, base_url)
        await check_server(handler, method_not_allowed, method.value, base_url)


async def unsupported_http_version(socket, url, version):
    """Expect from socket a HTTP response with status 505."""
    async with connect(socket) as (reader, writer):
        await write_request(writer, f'GET {url} HTTP/{version}\r\n')
        status = await reader.readuntil(b'\r\n')
        assert status == b'HTTP/1.1 505 HTTP Version Not Supported\r\n'


@given(urls().filter(is_base_url).filter(has_usual_path), integers(10))
async def test_unsupported_http_version(base_url, version):
    with tmp_cert_file(()) as cert_file:
        handler = partial(handle, cert_file, base_url)
        await check_server(handler, unsupported_http_version,
                           base_url, version)
