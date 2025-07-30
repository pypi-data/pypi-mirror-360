"""entity classes for task entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config


class Event(AnyEntity):
    __regid__ = 'Event'

    fetch_attrs, cw_fetch_order = fetch_config(['title'])

    def dc_title(self):
        return self.title
