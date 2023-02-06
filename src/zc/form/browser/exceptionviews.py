##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Views for exceptions used by the Schema product."""

from html import escape

from zope import component
from zope import i18n
from zope import interface
from zope.exceptions.interfaces import UserError
from zope.formlib.interfaces import ConversionError
from zope.formlib.interfaces import IWidgetInputErrorView
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import ValidationError


@interface.implementer(IWidgetInputErrorView)
class AbstractErrorView:
    """Base error view."""

    def __init__(self, context, request):
        self.context, self.request = context, request

    def snippet(self):
        """Convert an invariant error to an html snippet."""
        msg = self.context.args[0]
        msg = i18n.translate(msg, context=self.request, default=msg)
        return '<span class="error">%s</span>' % escape(str(msg))


@component.adapter(ValidationError, IBrowserRequest)
class ValidationErrorView(AbstractErrorView):
    """An error view for ValidationError."""


@component.adapter(ConversionError, IBrowserRequest)
class ConversionErrorView(AbstractErrorView):
    """An error view for ConversionError."""


@component.adapter(UserError, IBrowserRequest)
class UserErrorView(AbstractErrorView):
    """An error view for UserErrorError."""
