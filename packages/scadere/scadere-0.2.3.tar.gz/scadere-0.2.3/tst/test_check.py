# Tests for the TLS client
# SPDX-FileCopyrightText: 2025 Nguyễn Gia Phong
# SPDX-License-Identifier: AGPL-3.0-or-later

from asyncio import get_running_loop, start_server
from datetime import datetime, timedelta, timezone
from io import StringIO
from ssl import Purpose, create_default_context as tls_context

from hypothesis import given
from pytest import mark
from trustme import CA

from scadere.check import base64_from_str, check, printable
from scadere.listen import parse_summary, str_from_base64

# Times in X.509 certificates are YYYYMMDDHHMMSSZ (RFC 5280)
SECONDS_AGO = datetime.now(timezone.utc).replace(microsecond=0)
NEXT_DAY = SECONDS_AGO + timedelta(days=1)
NEXT_WEEK = SECONDS_AGO + timedelta(days=7)


@given(...)
def test_base64(string: str):
    assert str_from_base64(base64_from_str(string)) == string


async def noop(reader, writer):
    """Do nothing."""
    writer.close()
    await writer.wait_closed()


async def get_cert_summary(netloc, after, ca):
    """Fetch TLS certificate expiration summary for netloc."""
    loop = get_running_loop()
    output = StringIO()
    await loop.run_in_executor(None, check, [netloc], after, output, ca)
    if not output.getvalue():
        return None
    summary, = map(parse_summary, output.getvalue().splitlines())
    return summary


@mark.parametrize('domain', ['localhost'])
@mark.parametrize('ca_name', ['trustme', '\x1f'])
@mark.parametrize('not_after', [SECONDS_AGO, NEXT_DAY, NEXT_WEEK])
@mark.parametrize('after', [NEXT_DAY, NEXT_WEEK])
@mark.parametrize('trust_ca', [False, True])
async def test_check(domain, ca_name, not_after, after, trust_ca):
    ctx = tls_context(Purpose.CLIENT_AUTH)
    ca = CA(organization_name=ca_name)
    cert = ca.issue_cert(domain, not_before=SECONDS_AGO, not_after=not_after)
    cert.configure_cert(ctx)
    ca.configure_trust(ctx)
    async with await start_server(noop, domain, ssl=ctx) as server:
        port = server.sockets[0].getsockname()[1]
        assert isinstance(port, int)
        summary = await get_cert_summary((domain, port), after,
                                         ca if trust_ca else None)
        if not trust_ca:
            assert summary[1] is None
            assert 'self-signed certificate' in summary[5]
        elif not_after == SECONDS_AGO:
            assert summary[1] is None
            assert 'certificate has expired' in summary[5]
        elif not printable(ca_name):
            assert summary[1] is None
            assert 'control character' in summary[5]
        elif not_after > after:
            assert summary is None
        else:
            assert summary[0] == SECONDS_AGO
            assert summary[1] == not_after
            assert summary[2] == domain
            assert summary[3] == port
            assert summary[5] == ca_name
