##############################################################################
#
# Copyright (c) 2003-2004 Zope Foundation and Contributors.
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
"""Combination widget"""

import zope.cachedescriptors.property
import zope.schema.interfaces
from zope import component
from zope.browserpage import ViewPageTemplateFile
from zope.formlib import namedtemplate
from zope.formlib.interfaces import IDisplayWidget
from zope.formlib.interfaces import IInputWidget
from zope.formlib.interfaces import WidgetInputError

from zc.form.browser.widgetapi import BaseWidget


class CombinationWidget(BaseWidget):

    widget_interface = IInputWidget

    @zope.cachedescriptors.property.Lazy
    def widgets(self):
        field = self.context
        res = []
        for f in field.fields:
            f = f.bind(self.context)
            w = component.getMultiAdapter((f, self.request,),
                                          self.widget_interface)
            w.setPrefix(self.name + ".")
            res.append(w)
        return res

    def setPrefix(self, prefix):
        super().setPrefix(prefix)
        for w in self.widgets:
            w.setPrefix(self.name + ".")

    def loadValueFromRequest(self):
        # the lack of an API to get the input value regardless of validation
        # is a significant problem.  The inability to clear errors is a
        # problem.
        field = self.context
        missing_value = field.missing_value
        widgets = self.widgets
        required_errors = []
        errors = []
        values = []
        any = False
        for w in widgets:
            try:
                val = w.getInputValue()
            except WidgetInputError as e:
                if isinstance(getattr(e, 'errors'),
                              zope.schema.interfaces.RequiredMissing):  # :-(
                    required_errors.append((w, e))
                else:
                    errors.append((w, e))
                val = w.context.missing_value
            values.append(val)
            any = any or val != w.context.missing_value
        if field.required or any or errors:
            errors.extend(required_errors)
        else:  # remove the required errors in the sub widgets
            for w, e in required_errors:
                w.error = lambda: None  # :-(
        if errors:
            if len(errors) == 1:
                errors = errors[0][1]
            else:
                errors = [e for widget, e in errors]
            self._error = WidgetInputError(
                self.context.__name__,
                self.label, errors)
            values = missing_value
        elif not any:
            values = missing_value
        else:
            values = tuple(values)
        return values

    template = namedtemplate.NamedTemplate('default')

    def render(self, value):
        field = self.context
        missing_value = field.missing_value
        if value is not missing_value:
            try:
                len_value = len(value)
            except (TypeError, AttributeError):
                value = missing_value
                self._set_values_on_widgets(value)
            else:
                if len_value != len(field.fields):
                    value = missing_value
                    self._set_values_on_widgets(value)
        if value is not missing_value:
            self._set_values_on_widgets(value)
        for w in self.widgets:  # XXX quick hack.
            if zope.schema.interfaces.IBool.providedBy(w.context):
                w.invert_label = True
            else:
                w.invert_label = False
        return self.template()

    def _set_values_on_widgets(self, values):
        hasInput = self.hasInput()
        for w, v in zip(self.widgets, values):
            if not hasInput or v != w.context.missing_value:
                w.setRenderedValue(v)


default_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('combinationwidget.pt'), CombinationWidget)


class CombinationDisplayWidget(CombinationWidget):

    widget_interface = IDisplayWidget
