"""Specific views for events

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.date import date_range

from cubicweb.predicates import is_instance
from cubicweb_web.view import EntityAdapter
from cubicweb_web.views.baseviews import TextView


class EventTextView(TextView):
    __select__ = is_instance('Event')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'%s: %s' % (entity.printable_value('diem'), entity.title))


class EventICalendarableAdapter(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = is_instance('Event')

    component = "event"

    @property
    def start(self):
        return self.entity.diem

    @property
    def stop(self):
        return self.entity.end_date


class EventICalendarViewsAdapter(EntityAdapter):
    """calendar views interface"""
    __regid__ = 'ICalendarViews'
    __select__ = is_instance('Event')

    def matching_dates(self, begin, end):
        """calendar views interface"""
        start = self.entity.diem
        stop = self.entity.end_date
        if not start and not stop:
            return []
        elif start and not stop:
            stop = start+1
        elif stop and not start:
            start = stop-1
        return list(date_range(start, stop))
