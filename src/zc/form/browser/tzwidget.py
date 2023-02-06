##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
# XXX argh.
import pytz.tzinfo

import zope.browserpage
import zope.formlib.interfaces
import zope.interface.common.idatetime
import zope.publisher.interfaces.browser
from zope import component
from zope import interface
from zope.interface.common.idatetime import ITZInfo
from zope.security.checker import NamesChecker

import zc.form.browser.mruwidget
import zc.form.interfaces


ALL_TIMEZONES = frozenset(pytz.all_timezones)

names = set(ITZInfo.names(all=True))
names.add('zone')
names.add('localize')
checker = NamesChecker(names)
pytz.UTC.__Security_checker__ = checker
pytz.tzinfo.BaseTzInfo.__Security_checker__ = checker
# end argh.


class TimeZoneWidget(zc.form.browser.mruwidget.MruSourceInputWidget):

    def getMostRecentlyUsedTerms(self):
        mru = super().getMostRecentlyUsedTerms()
        # add ones from locale
        territory = self.request.locale.id.territory
        if territory:
            try:
                choices = pytz.country_timezones(territory)
            except KeyError:
                pass
            else:
                already = {term.token for term in mru}
                additional = sorted(t for t in choices if t not in already)
                mru.extend(zc.form.interfaces.Term(t.replace('_', ' '), t)
                           for t in additional)
        return mru


@component.adapter(zc.form.interfaces.AvailableTimeZones,
                   zope.publisher.interfaces.browser.IBrowserRequest)
@interface.implementer(zope.formlib.interfaces.ISourceQueryView)
class TimeZoneQueryView:

    def __init__(self, source, request):
        self.context = source
        self.request = request

    _render = zope.browserpage.ViewPageTemplateFile('timezone_queryview.pt')

    def render(self, name):
        return self._render(field_name=name + '.searchstring',
                            button_name=name + '.search')

    def results(self, name):
        if not (name + '.search' in self.request):
            return None

        searchstring = self.request[name + '.searchstring'].lower()
        timezones = []
        searchstring = searchstring.strip().lower().replace(' ', '_')  # regex
        for tz in ALL_TIMEZONES:
            if searchstring in tz.lower():
                timezones.append(pytz.timezone(tz))
        return timezones
