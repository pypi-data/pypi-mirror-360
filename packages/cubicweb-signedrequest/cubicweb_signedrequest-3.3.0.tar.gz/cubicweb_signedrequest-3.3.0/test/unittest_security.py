# copyright 2013-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb import Unauthorized
from cubicweb.devtools.testlib import CubicWebTC


class SecurityTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            self.toto_eid = self.create_user(cnx, "toto").eid

    def test_other_user_no_token_read(self):
        with self.admin_access.client_cnx() as cnx:
            self.create_user(cnx, "babar")

        with self.new_access("toto").client_cnx() as cnx:
            cnx.create_entity("AuthToken", id="122")
            cnx.commit()
            rset = cnx.execute(
                "Any T WHERE AT token T, AT token_for_user U, U login %(login)s",
                {"login": "toto"},
            )
            self.assertTrue(rset)

        with self.new_access("babar").client_cnx() as cnx:
            rset = cnx.execute(
                "Any T WHERE AT token T, AT token_for_user U, U login %(login)s",
                {"login": "toto"},
            )
            self.assertFalse(rset)

    def test_user_token_add(self):
        with self.new_access("toto").client_cnx() as cnx:
            tokeneid = cnx.create_entity("AuthToken", id="122").eid
            cnx.commit()
            with self.assertRaises(Unauthorized):
                cnx.create_entity(
                    "AuthToken",
                    id="foo",
                    token="forbidden",
                    token_for_user=self.toto_eid,
                )
                cnx.commit()

        with self.admin_access.repo_cnx() as cnx:
            token = cnx.entity_from_eid(tokeneid)
            self.assertEqual(128, len(token.token))

    def test_user_token_modify(self):
        with self.new_access("toto").client_cnx() as cnx:
            token = cnx.create_entity("AuthToken", id="122")
            cnx.commit()
            cnx.execute("SET AT enabled True WHERE AT eid %(e)s", {"e": token.eid})
            cnx.commit()
            with self.assertRaises(Unauthorized):
                cnx.execute('SET AT token "babar" WHERE AT eid %(e)s', {"e": token.eid})
                cnx.commit()

    def test_user_token_delete(self):
        with self.new_access("toto").client_cnx() as cnx:
            token = cnx.create_entity("AuthToken")
            cnx.commit()
            cnx.execute("DELETE AuthToken T WHERE T eid %(e)s", {"e": token.eid})
            cnx.commit()

    def test_manager_do_enabled_modify(self):
        with self.new_access("toto").client_cnx() as cnx:
            token = cnx.create_entity("AuthToken", id="122")
            cnx.commit()

        with self.admin_access.repo_cnx() as cnx:
            token = cnx.entity_from_eid(token.eid)
            with self.assertRaises(Unauthorized):
                token.cw_set(enabled=True)
                cnx.commit()

    def test_manager_no_token_modify(self):
        with self.admin_access.client_cnx() as cnx:
            token = cnx.create_entity("AuthToken", id="122")
            cnx.commit()
            with self.assertRaises(Unauthorized):
                token.cw_set(token="babar")
                cnx.commit()

    def test_token_for_other_user_permissions(self):
        with self.admin_access.client_cnx() as cnx:
            babar_eid = self.create_user(cnx, "babar").eid
            babar_token_eid = cnx.create_entity(
                "AuthToken", id="ba", token_for_user=babar_eid
            ).eid
            cnx.commit()

        with self.new_access("toto").client_cnx() as cnx:
            with self.assertRaises(Unauthorized):
                # can't create token for someone else.
                cnx.create_entity("AuthToken", id="122", token_for_user=babar_eid)
                cnx.commit()
            cnx.rollback()
            cnx.create_entity("AuthToken", id="122", token_for_user=self.toto_eid)
            cnx.commit()

        # attempt to delete `token_for_user` relation has no effect ("toto"
        # can't read the AuthToken).
        with self.new_access("toto").client_cnx() as cnx:
            rset = cnx.execute(
                "DELETE T token_for_user B WHERE T token_for_user U,"
                ' U login "toto", B login "babar"'
            )
            cnx.commit()
            self.assertFalse(rset)
        with self.admin_access.repo_cnx() as cnx:
            rset = cnx.execute('Any T WHERE T token_for_user U, U login "babar"')
            self.assertTrue(rset)
            self.assertEqual(rset[0][0], babar_token_eid)

        # admin can change relation.
        with self.admin_access.client_cnx() as cnx:
            cnx.execute(
                "SET T token_for_user B WHERE T token_for_user U,"
                ' U login "toto", B login "babar"'
            )
            cnx.commit()


if __name__ == "__main__":
    import unittest

    unittest.main()
