##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Views for exceptions used by the Schema product

$Id: exceptionviews.py 3629 2005-10-06 21:01:27Z gary $
"""
from zope import interface, component, i18n
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.publisher.interfaces.browser import IBrowserRequest
from cgi import escape
from zope.schema.interfaces import ValidationError
from zope.app.form.interfaces import ConversionError
from zope.app.exception.interfaces import UserError

class AbstractErrorView(object):
    interface.implements(IWidgetInputErrorView)
    
    def __init__(self, context, request):
        self.context, self.request = context, request
    
    def snippet(self):
        """Convert an invariant error to an html snippet.
        
        >>> from zope.schema.interfaces import ValidationError
        >>> err = ValidationError(
        ... "Bad error!  Bad!")
        >>> view = ValidationErrorView(err, None)
        >>> view.snippet()
        '<span class="error">Bad error!  Bad!</span>'
        """
        msg = self.context.args[0]
        msg = i18n.translate(msg, context=self.request, default=msg)
        return '<span class="error">%s</span>' % escape(str(msg))

class ValidationErrorView(AbstractErrorView):
    component.adapts(ValidationError, IBrowserRequest)

class ConversionErrorView(AbstractErrorView):
    component.adapts(ConversionError, IBrowserRequest)

class UserErrorView(AbstractErrorView):
    component.adapts(UserError, IBrowserRequest)
