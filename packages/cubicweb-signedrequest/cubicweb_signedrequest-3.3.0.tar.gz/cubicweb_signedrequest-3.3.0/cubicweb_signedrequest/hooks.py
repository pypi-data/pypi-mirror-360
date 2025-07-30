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

from datetime import UTC, datetime, timedelta
from uuid import uuid4 as uuid

from cubicweb.predicates import is_instance
from cubicweb.server import hook

from cubicweb_signedrequest.authplugin import UserSecretKeyAuthentifier


class ServerStartupHook(hook.Hook):
    """register authentifier at startup"""

    __regid__ = "signedrequest.secretkeyinit"
    events = ("server_startup",)

    def __call__(self):
        self.debug("registering secret key authentifier")
        self.repo.system_source.add_authentifier(UserSecretKeyAuthentifier())


class CreateAuthTokenHook(hook.Hook):
    """Generate random secret token"""

    __regid__ = "signedrequest.createauthtoken"
    __select__ = hook.Hook.__select__ & is_instance("AuthToken")
    events = ("before_add_entity",)

    def __call__(self):
        edited = self.entity.cw_edited
        # generate token as a 128 chars len string
        token = "".join([uuid().hex for __ in range(4)])
        edited["token"] = token
        edited["id"] = edited.get("id") or str(uuid().hex)
        edited.setdefault("token_for_user", self._cw.user.eid)
        max_expiration_delay = self._cw.repo.config["token-max-expiration-delay"]
        if max_expiration_delay is not None:
            max_date = datetime.now(UTC) + timedelta(days=max_expiration_delay)

            edited["expiration_date"] = min(
                max_date, edited.get("expiration_date", max_date)
            )
