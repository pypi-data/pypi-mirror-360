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
"""plugin authentication retriever for signed request"""

from cubicweb import AuthenticationError
from cubicweb.predicates import anonymous_user
from cubicweb_web.controller import Controller
from cubicweb_web.views import uicfg
from cubicweb_web.views.authentication import NoAuthInfo, WebAuthInfoRetriever

from cubicweb_signedrequest.tools import (
    build_string_to_sign,
    get_credentials_from_headers,
    hash_content,
)

# web authentication info retriever ###########################################


class HttpRESTAuthRetriever(WebAuthInfoRetriever):
    """Authenticate by the Authorization http header"""

    __regid__ = "www-authorization"
    order = 0

    def authentication_information(self, req):
        """retrieve authentication information from the given request, raise
        NoAuthInfo if expected information is not found
        return token id, signed string and signature
        """
        self.debug("web authenticator building auth info")
        login, signature = self.parse_authorization_header(req)
        string_to_sign = build_string_to_sign(req, req.url())
        return login, {"signature": signature, "request": string_to_sign}

    def parse_authorization_header(self, req):
        """Return the token id and the request signature.

        They are retrieved from the http request headers "Authorization"
        """
        try:
            content = req.content
        except AttributeError:
            # XXX cw 3.15 compat
            content = req._twreq.content
        content.seek(0)
        sha512 = hash_content(content)
        content.seek(0)
        credentials = get_credentials_from_headers(req, sha512)
        if credentials is None:
            raise NoAuthInfo()
        return credentials.split(":", 1)

    def request_has_auth_info(self, req):
        signature = req.get_header("Authorization", None)
        return signature is not None

    def revalidate_login(self, req):
        return None

    def cleanup_authentication_information(self, req):
        # we found our header, but authentication failed; we don't want to fall
        # back to other retrievers or (especially) an anonymous login
        raise AuthenticationError()


# Tokens management ###########################################################

_afs = uicfg.autoform_section
_rctrl = uicfg.reledit_ctrl
_affk = uicfg.autoform_field_kwargs
_pvdc = uicfg.primaryview_display_ctrl

_afs.tag_attribute(("AuthToken", "token"), "main", "hidden")
_pvdc.tag_attribute(("AuthToken", "token"), {"vid": "verbatimattr"})

_rctrl.tag_attribute(("AuthToken", "id"), {"reload": True})
_affk.tag_attribute(("AuthToken", "id"), {"required": False})

_afs.tag_object_of(("*", "token_for_user", "CWUser"), "main", "hidden")


# Authentication test #########################################################
#
# currently, on sites where anonymous are allowed you'll get a 200 status code
# on request with bad Authorization header, making hard to know if the
# authorization succeeded or not, so one may use /authtest if he want to know.


class AuthTestFail(Controller):
    """Dumb controller to test signed request authentication on an
    anonymous allowed site"""

    __regid__ = "authtest"
    __select__ = anonymous_user()

    def publish(self, rset=None):
        raise AuthenticationError()


class AuthTestSuccess(Controller):
    __regid__ = "authtest"
    __select__ = ~anonymous_user()

    def publish(self, rset=None):
        return f"you are properly authenticated as {self._cw.user.login}"
