##############################################################################
#
# Copyright (c) 2003-2005 Zope Corporation and Contributors.
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
"""interfaces.py: interfaces for the package

$Id: interfaces.py 4634 2006-01-06 20:21:15Z fred $"""
import datetime
import pytz

from zope import interface, component, schema
import zope.publisher.interfaces.browser
import zope.schema.interfaces
import zope.app.form.browser.interfaces
from zc.form.i18n import _

class IExtendedField(zope.schema.interfaces.IField):

    constraints = schema.Tuple(
        title=_("Constraints"),
        description=_("""A tuple of callables taking the combination field
        and the value, that should raise an exception if the values do not
        match the constraint.  Can assume that value is not the missing_value,
        and has a len equal to the number of sub-fields."""))

    def default_getter(context):
        "returns the default value"

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
        "return value for option field"

class IUnionField(IExtendedField):
    u"""A field that may have one of many field types of values.  
    Order is important, in that the first field from left to right that
    validates a value is considered to be the "active" field."""
    
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
        u"returns first valid field for the given value, or None"

class ICombinationField(IExtendedField):
    u"""A field that describes a combination of two or more fields"""

    fields = schema.Tuple(
        title=_("Composite Fields"),
        description=_("""\
            The schema fields that may describe the data"""))

class IExtendedTextLineField(IExtendedField, zope.schema.interfaces.ITextLine):
    "TextLine field extended with IExtendedField capabilities"

class AvailableTimeZones(object):
    interface.implements(zope.schema.interfaces.ISource)

    def __contains__(self, value):
        return isinstance(value, datetime.tzinfo)

class Term:
    interface.implements(zope.schema.interfaces.ITitledTokenizedTerm)

    def __init__(self, title, token):
        self.title = title
        self.token = token

class TimeZoneTerms:
    """Term and value support needed by query widgets."""

    interface.implements(zope.app.form.browser.interfaces.ITerms)
    component.adapts(AvailableTimeZones,
                     zope.publisher.interfaces.browser.IBrowserRequest)

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
