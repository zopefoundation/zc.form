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
"""tests of custom widgets defined in Schema"""
import doctest
import re
import unittest

import zope.component.testing
import zope.traversing.adapters

from zope.schema import TextLine, Int
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.formlib.textwidgets import TextWidget, IntWidget
from zope.schema.interfaces import ITextLine, IInt
from zope.formlib.interfaces import IInputWidget
from zope.publisher.browser import TestRequest

from zope.configuration import xmlconfig
import zc.form.browser
from zc.form.field import Union
import zc.form.field
from zc.form.browser.unionwidget import UnionWidget

from zope import component
import zope.schema.interfaces
import zope.publisher.interfaces.browser


class TestUnionWidget(
        zope.component.testing.PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestUnionWidget, self).setUp()
        # XXX cheating: should not rely on these. :-/
        component.provideAdapter(
            TextWidget, (ITextLine, IBrowserRequest), IInputWidget)
        component.provideAdapter(
            IntWidget, (IInt, IBrowserRequest), IInputWidget)
        from zc.form.browser.unionwidget import default_template
        component.provideAdapter(default_template, name='default')
        component.provideAdapter(
            zope.traversing.adapters.DefaultTraversable,
            [None],
        )

    def test_render(self):
        request = TestRequest()
        field = Union(
            (TextLine(title=u"Name", min_length=5),
             Int(title=u"Age", min=0)),
            title=u"Simple Identifier",
            __name__='identifier')
        widget = UnionWidget(field, request)
        widget.setPrefix('field')
        output = widget()
        self.failUnless('<table' in output)
        self.failUnless('Age' in output)
        self.failUnless('Name' in output)
        self.failUnless(re.search(
            r'''type=['"]radio['"]''', output))
        self.failUnless(re.search(
            r'''name=['"]field.identifier['"]''', output))
        self.failUnless(re.search(
            r'''id=["']field.identifier-00['"]''', output))
        self.failUnless(re.search(
            r'''id=["']field.identifier-01['"]''', output))
        self.failUnless(re.search(
            r'''name=["']field.identifier.unioned_00['"]''', output))
        self.failUnless(re.search(
            r'''name=["']field.identifier.unioned_01['"]''', output))
        self.failIf(re.search(
            r'''id=["']field.identifier-02['"]''', output))
        self.failIf(re.search(
            r'''checked\s*=\s*['"]checked['"]''', output))
        field = Union(
            (TextLine(title=u"Name", min_length=5),
             Int(title=u"Age", min=0)),
            title=u"Simple Identifier",
            __name__='identifier',
            required=False)
        widget = UnionWidget(field, request)
        widget.setPrefix('field')
        output = widget()
        self.failUnless(re.search(
            r'''id=["']field.identifier-02['"]''', output))
        self.failUnless(re.search(
            r'''checked\s*=\s*['"]checked['"]''', output))

    def test_use_default_for_not_selected(self):
        # test use_default_for_not_selected = True
        request = TestRequest()
        # the default selection shoud be the the option field which has the
        # value of None
        field = Union(
            (zc.form.field.TextLine(
                title=u"New Password", missing_value=u'',
                default_getter=lambda x: u'secret password'),
             zc.form.field.Option(
                title=u"No Change", value_getter=lambda x: None)),
            title=u"Change Password",
            missing_value=u'',
            use_default_for_not_selected=True,
            __name__='identifier')
        widget = UnionWidget(field, request)
        widget.setPrefix('field')
        output = widget()
        # remove double whitespaces
        normalized_output = " ".join(output.split())

        # the value of the textline field should be the default_getter's
        # result
        value_attr_of_textline = re.search(
            '<input.*id="field.identifier.unioned_00".*(value=".*").*></div>',
            normalized_output).groups()[0]
        self.failUnless('secret password' in value_attr_of_textline)

        # the radio button of the option field should be selected
        radio_option_field = re.search(
            '<input.*id="field.identifier-01"(.*)/> </td>',
            normalized_output).groups()[0]
        self.failUnless('checked="checked"' in radio_option_field)

    def test_evaluate(self):
        request = TestRequest()
        request.form.update({
            'field.identifier-marker': 'x',
            'field.identifier.unioned_00': u'Foo Bar',
            'field.identifier': '0'})
        field = Union(
            (TextLine(title=u"Name", min_length=5),
             Int(title=u"Age", min=0)),
            title=u"Simple Identifier",
            __name__='identifier')
        widget = UnionWidget(field, request)
        widget.setPrefix('field')
        self.assertEquals(widget.loadValueFromRequest(), u'Foo Bar')


def zcml(s, execute=True):
    context = xmlconfig.file('meta.zcml',
                             package=zc.form.browser)
    return xmlconfig.string(s, context, execute=execute)


def pageSetUp(test):
    zope.component.testing.setUp(test)
    component.provideAdapter(
        zope.traversing.adapters.DefaultTraversable,
        [None],
    )


def test_suite():
    suite = unittest.makeSuite(TestUnionWidget)
    suite.addTest(doctest.DocFileSuite(
        'exceptionviews.rst',
        setUp=zope.component.testing.setUp,
        tearDown=zope.component.testing.tearDown))
    suite.addTest(
        doctest.DocFileSuite(
            'combinationwidget.rst',
            setUp=pageSetUp,
            tearDown=zope.component.testing.tearDown),)
    return suite
