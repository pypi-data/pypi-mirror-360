# -*- coding: utf-8 -*-
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
"""Set of HTML startup views. A startup view is global, e.g. doesn't apply to a
result set.
"""

__docformat__ = "restructuredtext en"

from cubicweb import _
from cubicweb.predicates import is_instance
from cubicweb_web import component


def has_rncs(entity):
    return entity.rncs is not None


def url_societecom(entity):
    url = 'http://www.societe.com/'
    if entity.rncs:
        url += 'cgi-bin/recherche?rncs=%s' % entity.rncs
    return url


def url_score3(entity):
    url = 'http://www.score3.fr/'
    if entity.rncs:
        url += 'entreprises.shtml?chaine=%s' % entity.rncs
    elif entity.name:
        url += 'entreprises.shtml?chaine=%s' % entity.name
    return url


def url_linkedin(entity):
    url = 'http://www.linkedin.com/companies/'
    if entity.name:
        url += entity.name
    return url


def url_viadeo(entity):
    url = 'http://www.viadeo.com/'
    if entity.name:
        url += 'recherche/transverse/index.jsp?queryString=%s&search=go' % entity.name
    return url


class CompanySeeAlso(component.EntityCtxComponent):
    __regid__ = 'company_seealso_box'
    __select__ = component.EntityCtxComponent.__select__ & is_instance('Company')
    title = _('This company on other sites')
    order = 25

    def render_body(self, w):
        self.append(self.link(u'Société.com', url_societecom(self.entity)))
        self.append(self.link(u'Score3.fr', url_score3(self.entity)))
        self.append(self.link(u'LinkedIn', url_linkedin(self.entity)))
        self.append(self.link(u'Viadeo', url_viadeo(self.entity)))
        self.render_items(w)
