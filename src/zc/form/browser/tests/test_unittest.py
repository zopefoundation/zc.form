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
import zope.publisher.interfaces.browser
import zope.schema.interfaces
import zope.traversing.adapters
from zope import component
from zope.formlib.interfaces import ConversionError
from zope.formlib.interfaces import IInputWidget
from zope.formlib.textwidgets import IntWidget
from zope.formlib.textwidgets import TextWidget
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import Int
from zope.schema import TextLine
from zope.schema.interfaces import IInt
from zope.schema.interfaces import ITextLine
from zope.schema.interfaces import ValidationError

import zc.form.browser
import zc.form.field
from zc.form.browser.exceptionviews import ValidationErrorView
from zc.form.browser.unionwidget import UnionWidget
from zc.form.field import Union


class TestUnionWidget(
        zope.component.testing.PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super().setUp()
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
            (TextLine(title="Name", min_length=5),
             Int(title="Age", min=0)),
            title="Simple Identifier",
            __name__='identifier')
        widget = UnionWidget(field, request)
        widget.setPrefix('field')
        output = widget()
        self.assertIn('<table', output)
        self.assertIn('Age', output)
        self.assertIn('Name', output)
        self.assertRegex(output, r'''type=['"]radio['"]''')
        self.assertRegex(output, r'''name=['"]field.identifier['"]''')
        self.assertRegex(output, r'''id=["']field.identifier-00['"]''')
        self.assertRegex(output, r'''id=["']field.identifier-01['"]''')
        self.assertRegex(
            output, r'''name=["']field.identifier.unioned_00['"]''')
        self.assertRegex(
            output, r'''name=["']field.identifier.unioned_01['"]''')
        self.assertNotRegex(output, r'''id=["']field.identifier-02['"]''')
        self.assertNotRegex(output, r'''checked\s*=\s*['"]checked['"]''')
        field = Union(
            (TextLine(title="Name", min_length=5),
             Int(title="Age", min=0)),
            title="Simple Identifier",
            __name__='identifier',
            required=False)
        widget = UnionWidget(field, request)
        widget.setPrefix('field')
        output = widget()
        self.assertRegex(output, r'''id=["']field.identifier-02['"]''')
        self.assertRegex(output, r'''checked\s*=\s*['"]checked['"]''')

    def test_use_default_for_not_selected(self):
        # test use_default_for_not_selected = True
        request = TestRequest()
        # the default selection shoud be the the option field which has the
        # value of None
        field = Union(
            (zc.form.field.TextLine(
                title="New Password", missing_value='',
                default_getter=lambda x: 'secret password'),
             zc.form.field.Option(
                title="No Change", value='no change')),
            title="Change Password",
            missing_value='',
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
        self.assertIn('secret password', value_attr_of_textline)

        # the radio button of the option field should be selected
        radio_option_field = re.search(
            '<input.*id="field.identifier-01"(.*)/> </td>',
            normalized_output).groups()[0]
        self.assertIn('checked="checked"', radio_option_field)

    def test_evaluate(self):
        request = TestRequest()
        request.form.update({
            'field.identifier-marker': 'x',
            'field.identifier.unioned_00': 'Foo Bar',
            'field.identifier': '0'})
        field = Union(
            (TextLine(title="Name", min_length=5),
             Int(title="Age", min=0)),
            title="Simple Identifier",
            __name__='identifier')
        widget = UnionWidget(field, request)
        widget.setPrefix('field')
        self.assertEqual(widget.loadValueFromRequest(), 'Foo Bar')


class TestInterfaces(unittest.TestCase):
    """Testing interfaces import."""

    def test_interfaces__import__1(self):
        """zope.form.browser.interfaces can be imported"""
        import zc.form.browser.interfaces  # noqa: F401


class TestValidationErrorView(unittest.TestCase):
    """Testing .exceptionviews.ValidationErrorView."""

    def test_exceptionviews__ValidationErrorView__1(self):
        """It converts an invariant error to an html snippet."""
        err = ValidationError("Bad error!  Bad!")
        view = ValidationErrorView(err, None)
        self.assertEqual(
            view.snippet(), '<span class="error">Bad error!  Bad!</span>')

    def test_exceptionviews__ValidationErrorView__2(self):
        """It converts also unicode an html snippet."""
        err = ValidationError("Fälscher!")
        view = ValidationErrorView(err, None)
        self.assertEqual(
            view.snippet(), '<span class="error">Fälscher!</span>')

    def test_exceptionviews__ValidationErrorView__3(self):
        """It quotes HTML characters correctly."""
        err = ValidationError("The <error> & me.")
        view = ValidationErrorView(err, None)
        self.assertEqual(
            view.snippet(),
            '<span class="error">The &lt;error&gt; &amp; me.</span>')

    def test_exceptionviews__ValidationErrorView__4(self):
        """It converts the exception argument of an ConversionError as well."""
        err = ConversionError(ValidationError("not valid"))
        view = ValidationErrorView(err, None)
        self.assertEqual(
            view.snippet(), '<span class="error">not valid</span>')


def pageSetUp(test):
    zope.component.testing.setUp(test)
    component.provideAdapter(
        zope.traversing.adapters.DefaultTraversable,
        [None],
    )


optionflags = (
    doctest.NORMALIZE_WHITESPACE
    | doctest.ELLIPSIS
    | doctest.REPORT_NDIFF
    | doctest.IGNORE_EXCEPTION_DETAIL
    | doctest.REPORT_ONLY_FIRST_FAILURE
)


def test_suite():
    return unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite(
            '../combinationwidget.rst',
            optionflags=optionflags,
            setUp=pageSetUp,
            tearDown=zope.component.testing.tearDown),
    ])
