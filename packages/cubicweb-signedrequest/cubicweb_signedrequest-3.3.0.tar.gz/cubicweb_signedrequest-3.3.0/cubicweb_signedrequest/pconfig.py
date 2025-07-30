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
"cubicweb-signedrequest pyramid_cubiweb integration module"

import logging

from cubicweb import AuthenticationError
from pyramid.authentication import IAuthenticationPolicy
from zope.interface import implementer

from cubicweb_signedrequest.tools import (
    authenticate_user,
    build_string_to_sign,
    get_credentials_from_headers,
    hash_content,
)

logger = logging.getLogger(__name__)


def body_hash_tween_factory(handler, registry):
    """pyramid tween that add a body_hash attribute to the request with
    the sha512 sum of the body. This tween must be insterted before any
    body rewrite logic, otherwise we cannot check request's signature"""

    def body_hash(request):
        "compute and attach the sha512 sum of the body of a request"
        # code to be executed for each request before
        # the actual application code goes here
        request.body_hash = hash_content(request.body_file_seekable)
        request.body_file_seekable.seek(0)
        return handler(request)

    return body_hash


@implementer(IAuthenticationPolicy)
class SignedRequestAuthPolicy:
    """A pyramid AuthenticationPolicy to allow authentication via a valid
    Authentication header.

    """

    headers_to_sign = ("Content-SHA512", "Content-Type", "Date")

    def unauthenticated_userid(self, request):
        return None

    def authenticated_userid(self, request):
        logger.debug("authentication by %s", self.__class__.__name__)
        try:
            credentials = get_credentials_from_headers(request, request.body_hash)
        except AuthenticationError:
            credentials = None
        if credentials is None:
            return
        try:
            userid, signature = credentials.split(":", 1)
        except ValueError:
            logger.warning("authentication failure: invalid credentials")
            return
        repo = request.registry["cubicweb.repository"]
        signed_content = build_string_to_sign(request)
        with repo.internal_cnx() as cnx:
            user_eid = authenticate_user(cnx, userid, signed_content, signature)
        return user_eid

    def effective_principals(self, request):
        return ()

    def remember(self, request, principals, **kw):
        return ()

    def forget(self, request):
        return ()
