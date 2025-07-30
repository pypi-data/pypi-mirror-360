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
"""plugin authentication retriever"""

from cubicweb import AuthenticationError
from cubicweb.server.sources import native

from cubicweb_signedrequest.tools import authenticate_user


class UserSecretKeyAuthentifier(native.BaseAuthentifier):
    "Provide an authentication procedure based on a private key ``token``"

    def authenticate(self, session, login, **kwargs):
        """Authentication procedure.

        :login: identifier for the token (see ``AuthToken`` entity)

        Expected kwargs are:

        :signature: signature of the request.

        :request: canonicalized version of the request, used to
                  compute the signature
        """
        session.debug("authentication by %s", self.__class__.__name__)
        signature = kwargs.get("signature")
        signed_content = kwargs.get("request")
        if signature is None or signed_content is None:
            raise AuthenticationError("authentication failure")
        user_eid = authenticate_user(session, login, signed_content, signature)
        if user_eid is None:
            raise AuthenticationError("invalid credentials")
        return user_eid
