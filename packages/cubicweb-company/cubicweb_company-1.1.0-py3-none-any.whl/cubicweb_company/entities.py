# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of cubicweb-company.
#
# cubicweb-company is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# cubicweb-company is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""this contains the cube-specific entities' classes"""

__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import ITreeAdapter
from cubicweb.predicates import is_instance


class Company(AnyEntity):
    """customized class for Company entities"""
    __regid__ = 'Company'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])


class CompanyITreeAdapter(ITreeAdapter):
    __select__ = is_instance('Company')
    tree_relation = 'subsidiary_of'
