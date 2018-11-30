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
"""functional test harness for zc.mruwidget"""
from zope import interface, component
import doctest
import zc.form.browser
import zope.app.wsgi.testlayer
import zope.browser.interfaces
import zope.formlib.interfaces
import zope.schema.interfaces

colors = ['red', 'green', 'cerulean blue']


@interface.implementer(zope.schema.interfaces.ISource)
class AvailableColors(object):

    def __contains__(self, value):
        return value in colors


@interface.implementer(zope.schema.interfaces.ITitledTokenizedTerm)
class Term(object):

    def __init__(self, title, token):
        self.title = title
        self.token = token


@component.adapter(zope.schema.interfaces.ISource,
                   zope.publisher.interfaces.browser.IBrowserRequest)
@interface.implementer(zope.browser.interfaces.ITerms)
class ColorTerms(object):
    """Term and value support needed by query widgets."""

    def __init__(self, source, request):
        self.request = request
        self.source = source

    def getTerm(self, value):
        if value not in self.source:
            raise LookupError
        token = value + '_token'
        title = value.capitalize()
        return Term(title, token)

    def getValue(self, token):
        return token.split('_')[0]


@component.adapter(zope.schema.interfaces.ISource,
                   zope.publisher.interfaces.browser.IBrowserRequest)
@interface.implementer(zope.formlib.interfaces.ISourceQueryView)
class SimpleColorSourceQueryView(object):

    def __init__(self, source, request):
        self.context = source
        self.request = request

    def render(self, name):
        return '<query view for colors>'

    def results(self, name):
        if not (name + '.search' in self.request):
            return None
        searchstring = self.request[name + '.searchstring']
        return [c for c in colors if searchstring in c]


ZCFormLayer = zope.app.wsgi.testlayer.BrowserLayer(zc.form.browser)


def setUp(test):
    component.provideAdapter(ColorTerms)
    component.provideAdapter(SimpleColorSourceQueryView)


def test_suite():
    suite = doctest.DocFileSuite(
        "mruwidget.rst",
        globs={'AvailableColors': AvailableColors(),
               'getRootFolder': ZCFormLayer.getRootFolder},
        optionflags=(doctest.NORMALIZE_WHITESPACE
                     | doctest.ELLIPSIS
                     | doctest.REPORT_ONLY_FIRST_FAILURE
                     | doctest.IGNORE_EXCEPTION_DETAIL
                     | doctest.REPORT_NDIFF),
        setUp=setUp,
    )
    suite.layer = ZCFormLayer
    return suite
