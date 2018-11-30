===================
 CombinationWidget
===================

The combinationwidget collects two or more subfields to provide a convenient
way to specify a sequence of values.

Rendering the widget returns a table with the subfields::

    >>> from zc.form.browser.combinationwidget import (
    ...     CombinationWidget, CombinationDisplayWidget, default_template)
    >>> from zope import component, interface
    >>> component.provideAdapter(default_template, name='default')
    >>> from zc.form.field import Combination, OrderedCombinationConstraint
    >>> from zope.schema import Int
    >>> from zope.schema.interfaces import IInt
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from zope.formlib.interfaces import IInputWidget
    >>> from zope.formlib.textwidgets import IntWidget
    >>> component.provideAdapter(
    ...     IntWidget, (IInt, IBrowserRequest), IInputWidget)
    >>> from zope import interface
    >>> class IDemo(interface.Interface):
    ...     acceptable_count = Combination(
    ...         (Int(title=u'Minimum', required=True, min=0),
    ...          Int(title=u'Maximum', required=False)),
    ...         title=u'Acceptable Count',
    ...         required=False,
    ...         constraints=(OrderedCombinationConstraint(),))
    ...
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> widget = CombinationWidget(IDemo['acceptable_count'], request)
    >>> widget.setPrefix('field')
    >>> widget.loadValueFromRequest() # None
    >>> print(widget())
    <input type='hidden' name='field.acceptable_count-marker' value='x' />
    <table class="combinationFieldWidget">
      <tr>
        <td class="label">
          <label for="field.acceptable_count.combination_00">
            <span class="required">*</span><span>Minimum</span>
          </label>
        </td>
        <td class="field">
          <div class="widget"><input class="textType"
            id="field.acceptable_count.combination_00"
            name="field.acceptable_count.combination_00" size="10" type="text"
            value=""  />
          </div>
        </td>
      </tr>
      <tr>
        <td class="label">
          <label for="field.acceptable_count.combination_01">
            <span>Maximum</span>
          </label>
        </td>
        <td class="field">
          <div class="widget"><input class="textType"
            id="field.acceptable_count.combination_01"
            name="field.acceptable_count.combination_01" size="10" type="text"
            value=""  />
          </div>
        </td>
      </tr>
    </table>

Setting the appropriate values in the Request lets the widget correctly read
the specified value::

    >>> request.form['field.acceptable_count-marker'] = 'x'
    >>> request.form['field.acceptable_count.combination_00'] = '10'
    >>> request.form['field.acceptable_count.combination_01'] = ''
    >>> widget = CombinationWidget(IDemo['acceptable_count'], request)
    >>> widget.setPrefix('field')
    >>> widget.getInputValue()
    (10, None)
    >>> print(widget())
    <...
    ...<input class="textType" id="field.acceptable_count.combination_00"
              name="field.acceptable_count.combination_00" size="10" type="text"
              value="10" />...
    ...<input class="textType" id="field.acceptable_count.combination_01"
              name="field.acceptable_count.combination_01" size="10" type="text"
              value="" />...


The field is fine with empty values, because it is not required::

    >>> request.form['field.acceptable_count-marker'] = 'x'
    >>> request.form['field.acceptable_count.combination_00'] = ''
    >>> request.form['field.acceptable_count.combination_01'] = ''
    >>> widget = CombinationWidget(IDemo['acceptable_count'], request)
    >>> widget.setPrefix('field')
    >>> widget.getInputValue() # None
    >>> print(widget())
    <...
    ...<input class="textType" id="field.acceptable_count.combination_00"
              name="field.acceptable_count.combination_00" size="10" type="text"
              value="" />...
    ...<input class="textType" id="field.acceptable_count.combination_01"
              name="field.acceptable_count.combination_01" size="10" type="text"
              value="" />...
    >>> bool(widget.error())
    False
    >>> bool(widget.widgets[0].error())
    False

If the optional value is filled in and the required one is not, though, there
are errors::

    >>> request.form['field.acceptable_count-marker'] = 'x'
    >>> request.form['field.acceptable_count.combination_00'] = ''
    >>> request.form['field.acceptable_count.combination_01'] = '10'
    >>> widget = CombinationWidget(IDemo['acceptable_count'], request)
    >>> widget.setPrefix('field')
    >>> widget.getInputValue()
    Traceback (most recent call last):
    WidgetInputError: ('acceptable_count', u'Acceptable Count',
    WidgetInputError('combination_00', u'Minimum',
    RequiredMissing('combination_00')))
    >>> import zope.formlib.interfaces
    >>> import zope.publisher.interfaces.browser
    >>> @interface.implementer(zope.formlib.interfaces.IWidgetInputErrorView)
    ... @component.adapter(zope.formlib.interfaces.WidgetInputError,
    ...     zope.publisher.interfaces.browser.IBrowserRequest)
    ... class SnippetView(object):
    ...
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...         self.request = request
    ...     def snippet(self):
    ...         return self.context.doc()
    ...
    >>> component.provideAdapter(SnippetView)
    >>> print(widget())
    <...
    ...<input class="textType" id="field.acceptable_count.combination_00"
              name="field.acceptable_count.combination_00" size="10"
              type="text" value="" />...
    ...Required input is missing...
    ...<input class="textType" id="field.acceptable_count.combination_01"
              name="field.acceptable_count.combination_01" size="10"
              type="text" value="10" />...
    >>> print(widget.error())
    Required input is missing.
    >>> print(widget.widgets[0].error())
    Required input is missing.

Similarly, if the field's constraints are not met, the widget shows errors::

    >>> request.form['field.acceptable_count-marker'] = 'x'
    >>> request.form['field.acceptable_count.combination_00'] = '20'
    >>> request.form['field.acceptable_count.combination_01'] = '10'
    >>> widget = CombinationWidget(IDemo['acceptable_count'], request)
    >>> widget.setPrefix('field')
    >>> widget.getInputValue()
    Traceback (most recent call last):
    WidgetInputError: ('acceptable_count', u'Acceptable Count',
    MessageValidationError(u'${minimum} ...
    >>> print(widget())
    <...
    ...input class="textType" id="field.acceptable_count.combination_00"
              name="field.acceptable_count.combination_00" size="10"
              type="text" value="20" />...
    ...<input class="textType" id="field.acceptable_count.combination_01"
              name="field.acceptable_count.combination_01" size="10"
              type="text" value="10" />...
    >>> print(widget.error())
    ${minimum} must be less than or equal to ${maximum}.


There's also a display version of the widget::

    >>> request = TestRequest()
    >>> from zope.formlib.widget import DisplayWidget
    >>> from zope.formlib.interfaces import IDisplayWidget
    >>> component.provideAdapter(
    ...     DisplayWidget, (IInt, IBrowserRequest), IDisplayWidget)
    >>> widget = CombinationDisplayWidget(IDemo['acceptable_count'], request)
    >>> widget.setPrefix('field')
    >>> widget.setRenderedValue(('10', '2'))
    >>> print(widget())
    <input type='hidden' name='field.acceptable_count-marker' value='x' />
        <table class="combinationFieldWidget">
          <tr>
                  <td class="label">
                    <label for="field.acceptable_count.combination_00">
                      <span>Minimum</span>
                    </label>
                  </td>
              <td class="field">
                <div class="widget">10
                </div>
              </td>
          </tr>
          <tr>
                  <td class="label">
                    <label for="field.acceptable_count.combination_01">
                      <span>Maximum</span>
                    </label>
                  </td>
              <td class="field">
                <div class="widget">2
                </div>
              </td>
          </tr>
        </table>

In case of a wrong amount of parameters, the missing_value is used::

    >>> field = IDemo['acceptable_count']
    >>> field.missing_value=('23', '42')
    >>> widget = CombinationDisplayWidget(field, request)
    >>> widget.setPrefix('field')
    >>> widget.setRenderedValue(('10', '2', '3'))
    >>> print(widget())
    <input type='hidden' name='field.acceptable_count-marker' value='x' />
        <table class="combinationFieldWidget">
          <tr>
                  <td class="label">
                    <label for="field.acceptable_count.combination_00">
                      <span>Minimum</span>
                    </label>
                  </td>
              <td class="field">
                <div class="widget">23
                </div>
              </td>
          </tr>
          <tr>
                  <td class="label">
                    <label for="field.acceptable_count.combination_01">
                      <span>Maximum</span>
                    </label>
                  </td>
              <td class="field">
                <div class="widget">42
                </div>
              </td>
          </tr>
        </table>

In case the parameter is not a sequence, the missing_value is used::

    >>> widget = CombinationDisplayWidget(field, request)
    >>> widget.setPrefix('field')
    >>> widget.setRenderedValue(10)
    >>> print(widget())
    <input type='hidden' name='field.acceptable_count-marker' value='x' />
        <table class="combinationFieldWidget">
          <tr>
                  <td class="label">
                    <label for="field.acceptable_count.combination_00">
                      <span>Minimum</span>
                    </label>
                  </td>
              <td class="field">
                <div class="widget">23
                </div>
              </td>
          </tr>
          <tr>
                  <td class="label">
                    <label for="field.acceptable_count.combination_01">
                      <span>Maximum</span>
                    </label>
                  </td>
              <td class="field">
                <div class="widget">42
                </div>
              </td>
          </tr>
        </table>

The order of label and field are inverted in case of boolean::

    >>> request = TestRequest()
    >>> from zope.schema import Bool
    >>> from zope.schema.interfaces import IBool
    >>> from zope.formlib.boolwidgets import CheckBoxWidget
    >>> from zope.formlib.widget import DisplayWidget
    >>> from zope.formlib.interfaces import IDisplayWidget
    >>> component.provideAdapter(
    ...     CheckBoxWidget, (IBool, IBrowserRequest), IInputWidget)
    >>> class IBoolDemo(interface.Interface):
    ...     choices = Combination(
    ...         (Bool(title=u'first'),
    ...          Bool(title=u'second')),
    ...         title=u'Choices',
    ...         required=False,)

    >>> widget = CombinationWidget(IBoolDemo['choices'], request)
    >>> widget.setPrefix('field')
    >>> print(widget())
    <input type='hidden' name='field.choices-marker' value='x' />
        <table class="combinationFieldWidget">
          <tr>
                <td></td>
              <td class="field">
                <div class="widget"><input class="hiddenType" id="field.choices.combination_00.used" name="field.choices.combination_00.used" type="hidden" value="" /> <input class="checkboxType" id="field.choices.combination_00" name="field.choices.combination_00" type="checkbox" value="on"  />
                  <span>first</span>
                </div>
              </td>
          </tr>
          <tr>
                <td></td>
              <td class="field">
                <div class="widget"><input class="hiddenType" id="field.choices.combination_01.used" name="field.choices.combination_01.used" type="hidden" value="" /> <input class="checkboxType" id="field.choices.combination_01" name="field.choices.combination_01" type="checkbox" value="on"  />
                  <span>second</span>
                </div>
              </td>
          </tr>
        </table>

