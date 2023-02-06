##############################################################################
#
# Copyright (c) 2003-2005 Zope Foundation and Contributors.
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
import datetime

import pytz

import zope.browser.interfaces
import zope.publisher.interfaces.browser
import zope.schema.interfaces
from zope import component
from zope import interface
from zope import schema

from zc.form.i18n import _


class IExtendedField(zope.schema.interfaces.IField):

    constraints = schema.Tuple(
        title=_("Constraints"),
        description=_("""A tuple of callables taking the combination field
        and the value, that should raise an exception if the values do not
        match the constraint.  Can assume that value is not the missing_value,
        and has a len equal to the number of sub-fields."""))

    def default_getter(context):
        """Return the default value."""

    default = interface.Attribute(
        """if default_getter has been set, returns the result of that call;
        otherwise returns whatever value has been set as the default.""")


class IOptionField(IExtendedField):
    """Field with excatly one predefined value

    Caution: The value will not get displayed by the widget of this field.
    """

    value = interface.Attribute(
        """the value for this field; one and only one of value and
        value_getter must be non-None""")

    value_getter = interface.Attribute(
        """a callable, taking a context, return the option's value; or None.
        one and only one of value and value_getter must be non-None""")

    identity_comparison = schema.Bool(
        description=_("""Whether validation comparison should be identity
        (as opposed to equality) based"""))

    def getValue():
        """Return value for option field."""


class IUnionField(IExtendedField):
    """A field that may have one of many field types of values.

    Order is important, in that the first field from left to right that
    validates a value is considered to be the "active" field.
    """

    fields = schema.Tuple(
        title=_("Composite Fields"),
        description=_("""\
            The possible schema fields that may describe the data"""))

    use_default_for_not_selected = schema.Bool(
        description=_(
            """When displaying the Union field in the browser the fields
            which are not selected will have no value (i. e. the field's
            missing_value.

            With this attribute set the default value of the field will
            be displayed instead.

            Default: False"""))

    def validField(value):
        """Return first valid field for the given value, or None"""


class ICombinationField(IExtendedField):
    """A field that describes a combination of two or more fields"""

    fields = schema.Tuple(
        title=_("Composite Fields"),
        description=_("""\
            The schema fields that may describe the data"""))


class IExtendedTextLineField(IExtendedField, zope.schema.interfaces.ITextLine):
    """TextLine field extended with IExtendedField capabilities"""


@interface.implementer(zope.schema.interfaces.ISource)
class AvailableTimeZones:

    def __contains__(self, value):
        return isinstance(value, datetime.tzinfo)


@interface.implementer(zope.schema.interfaces.ITitledTokenizedTerm)
class Term:

    def __init__(self, title, token):
        self.title = title
        self.token = token


@component.adapter(AvailableTimeZones,
                   zope.publisher.interfaces.browser.IBrowserRequest)
@interface.implementer(zope.browser.interfaces.ITerms)
class TimeZoneTerms:
    """Term and value support needed by query widgets."""

    def __init__(self, source, request):
        self.request = request

    def getTerm(self, value):
        token = value.zone
        title = token.replace('_', ' ')
        return Term(title, token)

    def getValue(self, token):
        return pytz.timezone(token)


class IHTMLSnippet(zope.schema.interfaces.IText):
    """HTML excerpt that can be placed within an HTML document's body element.

    Snippet should have no dangling open tags.

    XHTML preferred; field may have version attribute in future.
    """


class IHTMLDocument(zope.schema.interfaces.IText):
    """HTML Document.

    XHTML preferred; field may have version attribute in future.
    """
