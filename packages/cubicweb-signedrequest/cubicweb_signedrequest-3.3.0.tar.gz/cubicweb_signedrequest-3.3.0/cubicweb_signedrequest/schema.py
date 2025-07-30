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

"""cubicweb-signedrequest schema"""

try:
    from cubicweb import _
except ImportError:
    _ = unicode  # noqa

from cubicweb.schema import ERQLExpression, RRQLExpression
from yams.buildobjs import Boolean, EntityType, RelationDefinition, String, TZDatetime


class AuthToken(EntityType):
    """Authentication token"""

    __permissions__ = {
        "read": ("managers", ERQLExpression("X token_for_user U")),
        "update": (ERQLExpression("X token_for_user U"),),
        "add": ("managers", ERQLExpression("X token_for_user U")),
        "delete": ("managers", ERQLExpression("X token_for_user U")),
    }
    id = String(
        maxsize=128,
        required=True,
        unique=True,
        description=_("identifier for the token (must be unique)"),
    )
    enabled = Boolean(required=True, default=False)
    token = String(
        maxsize=128,
        required=True,
        description=_("secret token"),
        # use default 'read' permission as RQL expressions are not
        # allowed in 'read' permission but rely on entity type
        # permissions anyways.
        __permissions__={
            "read": (
                "managers",
                "users",
            ),
            "add": (),
            "update": (),
        },
    )
    expiration_date = TZDatetime(
        description=_("auth token expiration date"),
        __permissions__={
            "read": (
                "managers",
                "users",
            ),
            "add": (
                "managers",
                "users",
            ),
            "update": (),
        },
    )
    last_time_used = TZDatetime(
        description=_("last time used"),
        __permissions__={
            "read": (
                "managers",
                "users",
            ),
            "add": (),
            "update": (),
        },
    )


class token_for_user(RelationDefinition):
    __permissions__ = {
        "read": (
            "managers",
            "users",
            "guests",
        ),
        "delete": ("managers", RRQLExpression("S token_for_user U")),
        "add": ("managers", "users"),
    }
    subject = "AuthToken"
    object = "CWUser"
    cardinality = "1*"
    inlined = True
    composite = "object"
