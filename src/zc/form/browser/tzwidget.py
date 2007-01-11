##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""timezone widget

$Id: tzwidget.py 3872 2005-11-05 04:41:55Z gary $
"""
import pytz

from zope import interface, component
import zope.publisher.interfaces.browser
from zope.app import pagetemplate
import zope.interface.common.idatetime

import zc.form.browser.mruwidget
import zc.form.interfaces

ALL_TIMEZONES = frozenset(pytz.all_timezones)

# XXX argh.
import pytz.tzinfo
from zope.security.checker import NamesChecker
from zope.interface.common.idatetime import ITZInfo
names = set(ITZInfo.names(all=True))
names.add('zone')
names.add('localize')
checker = NamesChecker(names)
pytz.UTC.__Security_checker__ = checker
pytz.tzinfo.BaseTzInfo.__Security_checker__ = checker
# end argh.

class TimeZoneWidget(zc.form.browser.mruwidget.MruSourceInputWidget):
        
    def getMostRecentlyUsedTerms(self):
        mru = super(TimeZoneWidget, self).getMostRecentlyUsedTerms()
        # add ones from locale
        territory = self.request.locale.id.territory
        if territory:
            try:
                choices = pytz.country_timezones(territory)
            except KeyError:
                pass
            else:
                already = set(term.token for term in mru)
                additional = sorted(t for t in choices if t not in already)
                mru.extend(zc.form.interfaces.Term(t.replace('_', ' '), t)
                             for t in additional)
        return mru

class TimeZoneQueryView(object):
    interface.implements(
            zope.app.form.browser.interfaces.ISourceQueryView)

    component.adapts(zc.form.interfaces.AvailableTimeZones,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        self.context = source
        self.request = request

    _render = pagetemplate.ViewPageTemplateFile('timezone_queryview.pt')
    def render(self, name):
        return self._render(field_name=name+'.searchstring',
                            button_name=name+'.search')

    def results(self, name):
        if not (name+'.search' in self.request):
            return None

        searchstring = self.request[name+'.searchstring'].lower()
        timezones = []
        searchstring = searchstring.strip().lower().replace(' ', '_') # regex
        for tz in ALL_TIMEZONES:
            if searchstring in tz.lower():
                timezones.append(pytz.timezone(tz))
        return timezones
