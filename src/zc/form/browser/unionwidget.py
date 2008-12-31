##############################################################################
#
# Copyright (c) 2003-2004 Zope Corporation and Contributors.
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
"""Union widget

$Id: unionwidget.py 4634 2006-01-06 20:21:15Z fred $
"""

from zope import component
from zope.app.form.interfaces import WidgetInputError

from widgetapi import BaseWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.pagetemplate import ViewPageTemplateFile

from zope.formlib import namedtemplate

import zc.form.interfaces

from zc.form.i18n import _


class CompositeOptionWidget(BaseWidget):
    def __call__(self):
        return None

class NotChosenWidget(object):
    error = name = None
    required = False

    def __init__(self, label, hint):
        self.label = label
        self.hint = hint

    def __call__(self):
        return None

class UnionWidget(BaseWidget):
    
    _field_index = None
    
    no_value_label = _('union_field_label-no_value', "Not specified")
    no_value_hint = _('union_field_hint-no_value', '')
    
    def loadValueFromRequest(self):
        field = self.context
        missing_value = field.missing_value
        value = self.request.form.get(self.name)
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = missing_value
        else:
            if value >= len(field.fields):
                value = missing_value
            else:
                self._field_index = value
                # value should be an int index of the active field
                active = field.fields[value].bind(self.context)
                if zc.form.interfaces.IOptionField.providedBy(active):
                    return active.getValue()
                widget = component.getMultiAdapter(
                    (active, self.request), IInputWidget)
                widget.required = widget.context.required = self.required
                widget.setPrefix(self.name)
                try:
                    return widget.getInputValue()
                except WidgetInputError, e:
                    # recast with our name and title
                    self._error = WidgetInputError(
                        self.context.__name__,
                        self.label,
                        e.errors)
        return missing_value
    
    template = namedtemplate.NamedTemplate('default')
    
    def render(self, value):
        # choices = ({selected, identifier, widget},)
        # widget may be None, name may be None.
        field = self.context
        missing_value = field.missing_value
        choices = []
        field_index = self._field_index
        if field_index is not None:
            chosen_field = field.fields[self._field_index]
        elif value is not missing_value:
            chosen_field = field.validField(value)
        else:
            chosen_field = None
        for ix, inner_field in enumerate(field.fields):
            selected = inner_field is chosen_field
            inner = inner_field.bind(field.context)
            identifier = "%s-%02d" % (self.name, ix)
            if zc.form.interfaces.IOptionField.providedBy(inner):
                widget = CompositeOptionWidget(inner, self.request)
            else:
                widget = component.getMultiAdapter(
                    (inner, self.request), IInputWidget)
                if selected:
                    widget.setRenderedValue(value)
                elif self._renderedValueSet():
                    if field.use_default_for_not_selected:
                        widget.setRenderedValue(inner.default)
                    else:
                        widget.setRenderedValue(inner.missing_value)
            widget.setPrefix(self.name)
            choices.append(
                {'selected': selected, 'identifier': identifier,
                 'widget': widget, 'value': unicode(ix)})
        if not field.required:
            ix += 1
            selected = chosen_field is None
            identifier = "%s-%02d" % (self.name, ix)
            widget = NotChosenWidget(self.no_value_label, self.no_value_hint)
            choices.append(
                {'selected': selected, 'identifier': identifier,
                 'widget': widget, 'value': unicode(ix)})
        return self.template(choices=choices)

default_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('unionwidget.pt'), UnionWidget)
