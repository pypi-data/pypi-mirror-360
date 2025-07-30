# copyright 2013-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""cubicweb-signedrequest tools for parsing and checking Authorization
headers
"""

import hashlib
import hmac
import logging
from datetime import UTC, datetime, timedelta
from email.utils import parsedate

from cubicweb import AuthenticationError

try:
    from hmac import compare_digest
except ImportError:
    # python 3.3 has hmac.compare_digest, but older versions don't.
    # this version should leak less timing information than the normal string
    # equality check
    # the expectation here is that both inputs are ascii strings of the same
    # length
    def compare_digest(expected, actual):
        if len(expected) != len(actual):
            return False
        result = 0
        for a, b in zip(expected, actual):
            result |= ord(a) ^ ord(b)
        return result == 0


log = logging.getLogger(__name__)

HEADERS_TO_SIGN = ("Content-SHA512", "Content-Type", "Date")
ALTERNATE_HEADERS = {"Date": ["X-Cubicweb-Date", "Date"]}


def get_replaceable_header_value(request, header_name, default=None):
    """
    Get the value for a header, looking at prioritized alternatives as required
    :param request: The request
    :param header_name: The name of the header
    :param default: The default value in case the header is not specified
    :return: The value of the header, or its alternatives
    """
    try:
        alternates = ALTERNATE_HEADERS[header_name]
        # we have a list of prioritized headers
        for alt_header_name in alternates:
            value = request.get_header(alt_header_name)
            if value is not None:
                return value
        return default
    except KeyError:
        # default behavior
        value = request.get_header(header_name)
        return value or default


def hash_content(content):
    """compute the sha512 sum of a file-like object's content

    Does NOT put the file's pos at the original position
    """
    sha512 = hashlib.sha512()
    while True:
        data = content.read(4096)
        if not data:
            break
        sha512.update(data)
    return sha512.hexdigest()


def get_credentials_from_headers(request, content_sha512):
    """Parse the request headers to retrieve the authentication credentials

    Returns the parsed credentials as a string '<tokenid>:<signature>' where
      <tokenid> is the identifier of the authentication token (AuthToken)
      <signature> is the signature of the content of the request, which must be
                  forged using the token's secret key to authenticate
                  the user linked with the AuthToken
    """
    header = get_replaceable_header_value(request, "Authorization", None)
    if header is None:
        log.debug("SIGNED REQUEST: error header is none")
        return
    try:
        method, credentials = header.split(None, 1)
    except ValueError:
        log.debug("SIGNED REQUEST: couldn't determine method from Authorization header")
        return
    if method != "Cubicweb":
        log.debug("SIGNED REQUEST: method is not Cubicweb")
        return
    if request.http_method() != "GET":
        if content_sha512 != get_replaceable_header_value(request, "Content-SHA512"):
            value = get_replaceable_header_value(request, "Content-SHA512")
            log.error(
                f"SIGNED REQUEST: wrong sha512, {content_sha512} != {value}",
            )
            raise AuthenticationError()
    date_header = get_replaceable_header_value(request, "Date")
    if date_header is None:
        raise AuthenticationError()
    try:
        date = datetime(*parsedate(date_header)[:6])
    except (ValueError, TypeError):
        log.error("SIGNED REQUEST: wrong date format")
        raise AuthenticationError()
    delta = abs(datetime.utcnow() - date)
    if delta > timedelta(0, 300):
        log.error("SIGNED REQUEST: date delta error")
        raise AuthenticationError()
    try:
        id, signature = credentials.split(":", 1)
        log.debug(f"SIGNED REQUEST: encoding info for {id}")
        return credentials
    except ValueError:
        log.exception("HTTP REST authenticator failed")
        raise AuthenticationError()


def build_string_to_sign(request, url=None, headers=None):
    """Return the string used to authenticate the request.

    The client must have provided a signed version of this string.

    The string is the concatenation of the http verb, url and values of the
    http request header fields specified in ``headers_to_sign``.
    """
    if headers is None:
        headers = HEADERS_TO_SIGN
    if url is None:
        url = request.url
    get_header = lambda field: get_replaceable_header_value(request, field, "")  # noqa
    return (request.http_method() + url + "".join(map(get_header, headers))).encode(
        "utf-8"
    )


def authenticate_user(session, tokenid, signed_content, signature):
    """Authenticate a user from a AuthToken id by checkig the
    request's signature is correct.

    :session: a cubicweb connection (usually a repo.internal_cnx()
              since it must have read access to the AuthToken)

    :tokenid: the AuthToken id belonging to the CWUser being authenticated

    :request: the http request

    :signature: the signature (usually extracted from the headers
                using get_credentals_from_headers), as *bytes*

    Returns the user's eid on success.

    """
    try:
        rset = session.execute(
            "Any U, K, D WHERE T token_for_user U, "
            "               T token K, "
            "               T enabled True, "
            "               T id %(id)s, "
            "               T expiration_date D, "
            "               U in_state ST, "
            '               ST name "activated"',
            {"id": tokenid},
        )
        if not rset:
            return
        assert len(rset) == 1
        user_eid, secret_key, expiration_date = rset[0]
        if expiration_date is not None and expiration_date < datetime.now(UTC):
            session.info(
                "tried to authenticate with expired token (id=%s)",
                tokenid,
            )
            return
        expected_signature = hmac.new(
            secret_key.encode("utf-8"), signed_content, digestmod="sha512"
        ).hexdigest()
        if compare_digest(expected_signature, signature):
            session.execute(
                "SET T last_time_used %(now)s WHERE T id %(id)s",
                {
                    "id": tokenid,
                    "now": datetime.utcnow().isoformat(),
                },
            )
            session.commit()
            return user_eid
        else:
            session.info(
                "request content signature check failed for %s (signed content is %r)",
                tokenid,
                signed_content,
            )
    except Exception as exc:
        session.debug("authentication failure (%s)", exc)
