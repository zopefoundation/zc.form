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
"""functional test harness for zc.mruwidget
"""
import os

from zope import interface, component
from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer
from zope.testing import doctest
import zope.schema.interfaces

colors = ['red', 'green', 'cerulean blue']

class AvailableColors(object):
    interface.implements(zope.schema.interfaces.ISource)

    def __contains__(self, value):
        return value in colors


class Term(object):
    interface.implements(zope.schema.interfaces.ITitledTokenizedTerm)

    def __init__(self, title, token):
        self.title = title
        self.token = token


class ColorTerms(object):
    """Term and value support needed by query widgets."""

    interface.implements(zope.app.form.browser.interfaces.ITerms)
    component.adapts(zope.schema.interfaces.ISource,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        self.request = request

    def getTerm(self, value):
        token = value + '_token'
        title = value.capitalize()
        return Term(title, token)

    def getValue(self, token):
        return token.split('_')[0]

class SimpleColorSourceQueryView(object):
    interface.implements(zope.app.form.browser.interfaces.ISourceQueryView)
    component.adapts(zope.schema.interfaces.ISource,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        self.context = source
        self.request = request

    def render(self, name):
        return '<query view for colors>'

    def results(self, name):
        if not (name+'.search' in self.request):
            return None
        searchstring = self.request[name+'.searchstring']
        return [c for c in colors if searchstring in c]


here = os.path.dirname(os.path.realpath(__file__))

ZCFormLayer = ZCMLLayer(
    os.path.join(here, "ftesting.zcml"), __name__, "ZCFormLayer")

def setUp(test):
    component.provideAdapter(ColorTerms)
    component.provideAdapter(SimpleColorSourceQueryView)
    

def test_suite():
    suite = FunctionalDocFileSuite("mruwidget.txt", 
            globs={'AvailableColors': AvailableColors()},
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            setUp=setUp,
            )
    suite.layer = ZCFormLayer
    return suite
