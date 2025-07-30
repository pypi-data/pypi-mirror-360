# copyright 2013-2025 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-signedrequest application packaging information"""

from importlib.metadata import metadata

modname = "signedrequest"
distname = "cubicweb-signedrequest"

cubicweb_metadata = metadata(distname).json

version = cubicweb_metadata["version"]
numversion = [int(number) for number in version.split(".")]

description = cubicweb_metadata["description"]
author, author_email = cubicweb_metadata["author_email"].split()
web = cubicweb_metadata["project_url"][-1].split(", ")[-1]
license = cubicweb_metadata["license"]
classifiers = cubicweb_metadata["classifier"]
