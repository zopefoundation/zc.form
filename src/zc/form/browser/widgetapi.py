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
"""Alternate base classes for IBrowserWidget implementations.

The base classes provided here implement the IBrowserWidget API and
provide a simpler API that derived classes are expected to implement.
"""

from xml.sax.saxutils import escape, quoteattr

from zope.interface import implements
from zope.schema.interfaces import ValidationError

from zope.app import zapi
from zope.app.form import InputWidget
from zope.app.form.browser.widget import BrowserWidget
from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.interfaces import IWidget, IInputWidget, WidgetInputError

from zc.form.i18n import _

_msg_missing_single_value_display = _(
    _("widget-missing-single-value-for-display"),   "")
_msg_missing_multiple_value_display = _(
    _("widget-missing-multiple-value-for-display"), "")

_msg_missing_single_value_edit = _(
    _("widget-missing-single-value-for-edit"),   "(no value)")
_msg_missing_multiple_value_edit = _(
    _("widget-missing-multiple-value-for-edit"), "(no value)")


class BaseWidget(BrowserWidget, InputWidget):
    # Note to previous users of widgetapi:
    # .translate -> ._translate; .__prefix -> ._prefix;  NullValue ->
    # ._data_marker; .__initial_value and .__calculated_value -> replaced
    # with ._data (because zope.app.form.utility.setUpWidget behavior changed
    # for the better)
    implements(IBrowserWidget, IInputWidget)

    _initialized = False
    _error = None
    _display = False # set this to True if you are using this for a display
                     # widget

    # Form management methods.
    # Subclasses should not need to override these.

    def getInputValue(self):
        if not self._initialized:
            self._initialize()

        if self._error is not None:
            raise self._error

        value = self._data
        field = self.context

        # allow missing values only for non-required fields
        if value == field.missing_value and not field.required:
            return value

        # value must be valid per the field contraints
        try:
            field.validate(value)
        except ValidationError, v:
            self._error = WidgetInputError(
                self.context.__name__, self.context.title, v)
            raise self._error
        return value

    def hasInput(self):
        if self._display:
            return False
        marker_name = self.name + "-marker"
        return marker_name in self.request.form

    def _initialize(self):
        self._initialized = True
        self.initialize()
        if not self._renderedValueSet():
            if self.hasInput():
                self._data = self.loadValueFromRequest()
            else: # self._data is self._data_marker but no input in request
                self._data = self.context.default

    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        change = field.query(content, self) != value
        if change:
            field.set(content, value)
            # Dynamic fields may change during a set, so re-get their value;
            # this is a larger Zope3 problem which is solved here for now.
            self._data = field.get(content)
        return change

    # Rendering methods:
    # (These should not need to be overridden.)

    def __call__(self):
        if not self._initialized:
            self._initialize()
        marker = self._get_marker()
        return marker + self.render(self._data)
    
    def hidden(self):
        if not self._initialized:
            self._initialize()
        marker = self._get_marker()
        return marker + self.renderHidden(self._data)

    def _get_marker(self):
        marker_name = self.name + "-marker"
        return "<input type='hidden' name='%s' value='x' />\n" % marker_name

    # API for subclasses to implement:

    def initialize(self):
        """Initialize internal data structures needed by the widget.

        This method should not load values from the request.

        Derived classes should call the base class initialize() before
        performing specialized initialization.  This requirement is
        waived for classes which inherit directly from, and *only*
        from, BaseWidget.
        """

    def loadValueFromRequest(self):
        """Load the value from data in the request."""
        raise NotImplementedError(
            "BaseWidget subclasses must implement loadValueFromRequest()")

    def render(self, value):
        raise NotImplementedError(
            "BaseWidget subclasses must implement render()")

    def renderHidden(self, value):
        "render a hidden widget"


class BaseVocabularyWidget(BaseWidget):

    query = None
    queryview = None

    def __init__(self, field, vocabulary, request):
        """Initialize the widget."""
        # only allow this to happen for a bound field
        assert field.context is not None
        self.vocabulary = vocabulary
        super(BaseVocabularyWidget, self).__init__(field, request)

    # Helpers used by the vocabulary widget machinery;
    # these should not be overriden.

    def setQuery(self, query, queryview):
        assert self.query is None
        assert self.queryview is None
        assert query is not None
        assert queryview is not None
        self.query = query
        self.queryview = queryview

        # Use of a hyphen to form the name for the query widget
        # ensures that it won't clash with anything else, since
        # field names are normally Python identifiers.
        queryview.setName(self.name + "-query")

    def initialize(self):
        """Make sure the query view has a chance to initialize itself."""
        if self.queryview is not None:
            self.queryview.initialize()

    def loadValueFromRequest(self):
        """Load the value from data in the request.

        If self.queryview is not None, this method is responsible for
        calling the query view's performAction() method with the value
        loaded, and returning the result::

            value = ...load value from request data...
            if self.queryview is not None:
                value = self.queryview.performAction(value)
            return value
        """
        return super(BaseVocabularyWidget, self).loadValueFromRequest()

    # Convenience method:

    def convertTokensToValues(self, tokens):
        """Convert a list of tokens to a list of values.

        If an invalid token is encountered, WidgetInputError is raised.
        """
        L = []
        for token in tokens:
            try:
                term = self.vocabulary.getTermByToken(token)
            except LookupError:
                raise WidgetInputError(
                    self.context.__name__,
                    self.context.title,
                    "token %r not found in vocabulary" % token)
            else:
                L.append(term.value)
        return L


class BaseVocabularyDisplay(BaseVocabularyWidget):
    
    _display = True

    def render(self, value):
        if value in (NullValue, None):
            # missing single value
            return self.translate(_msg_missing_single_value_display)
        else:
            return self.renderTerm(self.vocabulary.getTerm(value))

    def renderTerm(self, term):
        """Return textual presentation for term."""
        raise NotImplementedError("BaseVocabularyMultiDisplay subclasses"
                                  " must implement renderTerm()")

    def _get_marker(self):
        return ""


class BaseVocabularyMultiDisplay(BaseVocabularyDisplay):
    """Base class for display widgets of multi-valued vocabulary fields."""

    def render(self, value):
        if not value:
            # missing multiple value
            return self.translate(_msg_missing_multiple_value_display)
        else:
            pattern = ("<li>%s\n"
                       "    <input type='hidden' name=%s value=%s /></li>")
            vocabulary = self.vocabulary
            L = []
            name = quoteattr(self.name)
            for v in value:
                term = vocabulary.getTerm(v)
                L.append(pattern % (self.renderTerm(term), name,
                                    quoteattr(term.token)))
            return ("<%s class=%s id=%s>\n%s\n</%s>"
                    % (self.containerElementType,
                       quoteattr(self.containerCssClass),
                       quoteattr(self.name),
                       "\n".join(L),
                       self.containerElementType))

    containerCssClass = "values"


class BaseVocabularyBagDisplay(BaseVocabularyMultiDisplay):
    """Base class for display widgets of unordered multi-valued
    vocabulary fields."""

    containerElementType = "ul"


class BaseVocabularyListDisplay(BaseVocabularyMultiDisplay):
    """Base class for display widgets of ordered multi-valued
    vocabulary fields."""

    containerElementType = "ol"


class BaseQueryView(object):

    name = None
    widget = None
    _initialized = False

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # Methods called by the vocabulary widget construction machinery;
    # subclasses should not need to override these.

    def setName(self, name):
        assert not self._initialized
        assert not name.endswith(".")
        assert self.name is None
        self.name = name

    def setWidget(self, widget):
        assert not self._initialized
        assert self.widget is None
        assert widget is not None
        self.widget = widget

    # Methods which may be overriden by subclasses:

    def initialize(self):
        """Initialization which does not require reading the request.

        Derived classes should call the base class initialize() before
        performing specialized initialization.
        """
        # Should loading from the request happen here?
        assert self.name is not None
        assert self.widget is not None
        assert not self._initialized
        self._initialized = True

    def renderResults(self, value):
        """Render query results if we have any, otherwise return an
        empty string.
        """
        results = self.getResults()
        if results is None:
            return ""
        else:
            return self.renderQueryResults(results, value)

    # Methods which should be overriden by subclasses:

    def performAction(self, value):
        """Perform any modifications to the value based on user actions.

        This method should be overriden if the query view provides any
        actions which can modify the value of the field.
        """
        return value

    # Methods which must be overriden by subclasses:

    def getResults(self):
        """Perform the query, or return None.

        The return value should be None if there is no query to
        execute, or an object that can be rendered as a set of results
        by renderQueryResults().

        If the query results in an empty set of results, some value
        other than None should be used to represent the results so
        that renderQueryResults() can provide a helpful message.
        """
        raise NotImplementedError(
            "BaseQueryView subclasses must implement getResults()")

    def renderInput(self):
        """Render the input area of the query view."""
        raise NotImplementedError(
            "BaseQueryView subclasses must implement renderInput()")

    def renderQueryResults(self, results, value):
        """Render the results returned by getResults()."""
        raise NotImplementedError(
            "BaseQueryView subclasses must implement renderQueryResults()")
