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
"""cubicweb-signedrequest application package"""


def includeme(config):
    """Activate the signedrequest authentication policy in a
    cubicweb-pyramid instance.

    Usually called from the main cubicweb.pyramid.core configurator
    (see ``cubicweb.pyramid.core``).

    See also :ref:`defaults_module`

    """
    import pyramid.tweens

    from cubicweb_signedrequest.pconfig import SignedRequestAuthPolicy

    policy = SignedRequestAuthPolicy()
    config.add_tween(
        "cubicweb_signedrequest.pconfig.body_hash_tween_factory",
        under=pyramid.tweens.INGRESS,
    )

    # add some bw compat methods
    # these ease code factorization between pyramid related code and legacy one
    config.add_request_method(
        lambda req, header, default=None: req.headers.get(header, default),
        name="get_header",
        property=False,
        reify=False,
    )
    config.add_request_method(
        lambda req: req.method, name="http_method", property=False, reify=False
    )

    if config.registry.get("cubicweb.authpolicy") is None:
        err = (
            "signedrequest: "
            "the default cubicweb auth policy should be available"
            " via the 'cubicweb.authpolicy' registry config entry"
            "\n\n"
            "possible fix: "
            "in pyramid.ini, "
            "cubicweb.includes = cubicweb.pyramid.auth"
        )
        raise ValueError(err)

    # if we use (the default) a multiauth policy in CW, append
    # signedrequest to it
    mainpolicy = config.registry["cubicweb.authpolicy"]
    mainpolicy._policies.append(policy)
