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
"""fields

$Id: field.py 4634 2006-01-06 20:21:15Z fred $
"""
from zope import interface, i18n, schema, component
from zope.schema.interfaces import (
    ValidationError, WrongType, IField, IVocabularyTokenized)
from zope.interface.exceptions import DoesNotImplement
import zope.app.catalog.interfaces
import zope.index.text.queryparser
import zope.index.text.parsetree

from zc.form import interfaces
from zc.form.i18n import _

_no_unioned_field_validates = _(
    "No unioned field validates ${value}.")

_range_less_error = _("${minimum} must be less than ${maximum}.")
_range_less_equal_error = _(
    "${minimum} must be less than or equal to ${maximum}.")
_combination_wrong_size_error = _("The value has the wrong number of members")
_combination_not_a_sequence_error = _("The value is not a sequence")
_bad_query = _("Invalid query.")

# Union field that accepts other fields...

class MessageValidationError(ValidationError):
    "ValidationError that takes a message"

    def __init__(self, message, mapping=None):
        if mapping is not None:
            self.message = i18n.Message(message, mapping=mapping)
        else:
            self.message = message
        self.args = (message, mapping)
    def doc(self):
        return self.message

class BaseField(schema.Field):
    """Field with a callable as default and a tuple of constraints.

    >>> def secure_password(field, value):
    ...     if len(value) < 8:
    ...         raise schema.ValidationError, 'Password too short.'
    ...
    >>> class IDummy(interface.Interface):
    ...     suggested_password = BaseField(
    ...         title=u'Suggested Password',
    ...         default_getter=lambda context: u'asdf',
    ...         constraints=(secure_password, ))
    ... 
    >>> f = IDummy['suggested_password'].bind(None) # use None as context
    >>> interfaces.IExtendedField.providedBy(f)
    True
    >>> f.__name__
    'suggested_password'
    >>> f.title
    u'Suggested Password'
    >>> f.default
    u'asdf'
    >>> f.validate(u'123456789')
    >>> f.validate(u'asdf')
    Traceback (most recent call last):
    ...
    ValidationError: Password too short.
    """

    interface.implements(interfaces.IExtendedField)

    constraints = ()
    _default = default_getter = None
    
    def __init__(self, constraints=(), default_getter=None, **kw):
        self.constraints = constraints
        if default_getter is not None and 'default' in kw:
            raise TypeError(
                'may not specify both a default and a default_getter')
        super(BaseField, self).__init__(**kw)
        self.default_getter = default_getter

    def _validate(self, value):
        super(BaseField, self)._validate(value)
        if value != self.missing_value:
            for constraint in self.constraints:
                constraint(self, value)

    @apply
    def default():
        def getter(self):
            if self.default_getter is not None:
                return self.default_getter(self.context)
            else:
                return self._default
        def setter(self, value):
            assert self.default_getter is None
            self._default = value
        return property(getter, setter)

class Option(BaseField):

    interface.implements(interfaces.IOptionField)

    def __init__(self, value=None, value_getter=None, 
                 identity_comparison=False, **kw):
        self.value = value
        self.value_getter = value_getter
        self.identity_comparison = identity_comparison
        assert (value is None) ^ (value_getter is None)
        assert not kw.get('required')
        kw['required'] = False
        super(Option, self).__init__(**kw)

    def _validate(self, value):
        if value != self.missing_value:
            if self.identity_comparison:
                if self.getValue() is not value:
                    raise WrongType
            elif self.getValue() != value:
                raise WrongType

    def getValue(self):
        if self.value_getter is not None:
            return self.value_getter(self.context)
        else:
            return self.value

class Union(BaseField):
    """
    The Union field allows a schema field to hold one of many other field 
    types.  For instance, you might want to make a field that can hold
    a duration *or* a date, if you are working with a PIM app.  Or perhaps 
    you want to have a field that can hold a string from a vocabulary *or* a
    custom string.  Both of these examples can be accomplished in a variety of
    ways--the union field is one option.
    
    The second example is more easily illustrated.  Here is a union field that
    is a simple way of allowing "write-ins" in addition to selections from a 
    choice.  We'll be very explicit about imports, in part so this can be
    trivially moved to a doc file test.
    
    Notice as you look through the example that field order does matter: the
    first field as entered in the field list that validates is chosen as the
    validField; thus, even though the options in the Choice field would also 
    validate in a TextLine, the Choice field is identified as the "validField"
    because it is first.
    
    >>> class IDummy(interface.Interface):
    ...     cartoon_character = Union((
    ...         schema.Choice(
    ...             title=u'Disney',
    ...             description=u'Some tried-and-true Disney characters',
    ...             values=(u'Goofy',u'Mickey',u'Donald',u'Minnie')),
    ...         schema.TextLine(
    ...             title=u'Write-in',
    ...             description=u'Name your own!')),
    ...         required=True,
    ...         title=u'Cartoon Character',
    ...         description=u'Your favorite cartoon character')
    ... 
    >>> f = IDummy['cartoon_character']
    >>> interfaces.IUnionField.providedBy(f)
    True
    >>> f.__name__
    'cartoon_character'
    >>> isinstance(f.fields[0], schema.Choice)
    True
    >>> isinstance(f.fields[1], schema.TextLine)
    True
    >>> f.fields[0].__name__ != f.fields[1].__name__
    True
    >>> len(f.fields)
    2
    >>> f.title
    u'Cartoon Character'
    >>> f.validate(u'Goofy')
    >>> f.validField(u'Goofy') is f.fields[0]
    True
    >>> f.validate(u'Calvin')
    >>> f.validField(u'Calvin') is f.fields[1]
    True
    >>> f.validate(42)
    Traceback (most recent call last):
    ...
    MessageValidationError: (u'No unioned field validates ${value}.', {'value': 42})

    That's a working example.  Now lets close with a couple of examples that
    should fall over.

    You must union at least two fields:

    >>> f = Union((schema.TextLine(title=u'Foo Text Line!'),), title=u'Foo')
    Traceback (most recent call last):
    ...
    ValueError: union must combine two or more fields

    And, unsurprisingly, they must actually be fields:
    
    >>> from zope.interface.exceptions import DoesNotImplement
    >>> try:
    ...     f = Union(('I am not a number.', 'I am a free man!'), title=u'Bar')
    ... except DoesNotImplement:
    ...     print "Not a field"
    ... 
    Not a field

    Binding a union field also takes care of binding the contained fields:

    >>> context = object()
    >>> bound_f = f.bind(context)
    >>> bound_f.context is context
    True
    >>> bound_f.fields[0].context is context
    True
    >>> bound_f.fields[1].context is context
    True
    """
    
    interface.implements(interfaces.IUnionField)
    
    fields = ()
    use_default_for_not_selected = False
    
    def __init__(self, fields, use_default_for_not_selected=False, **kw):
        if len(fields) < 2:
            raise ValueError(_("union must combine two or more fields"))
        for ix, field in enumerate(fields):
            if not IField.providedBy(field):
                raise DoesNotImplement(IField)
            field.__name__ = "unioned_%02d" % ix
        self.fields = tuple(fields)
        self.use_default_for_not_selected = use_default_for_not_selected
        super(Union, self).__init__(**kw)

    def bind(self, object):
        clone = super(Union, self).bind(object)
        # We need to bind the fields too
        clone_fields = []
        for field in clone.fields:
            clone_fields.append(field.bind(object))
        clone_fields = tuple(clone_fields)
        clone.fields = clone_fields
        return clone

    def validField(self, value):
        "returns first valid field, or None"
        for field in self.fields:
            try:
                field.validate(value)
            except ValidationError:
                pass
            else:
                return field
    
    def _validate(self, value):
        if self.validField(value) is None:
            raise MessageValidationError(_no_unioned_field_validates, 
                                         {'value': value})

class OrderedCombinationConstraint(object):
    def __init__(self, may_be_equal=True, decreasing=False):
        self.may_be_equal = may_be_equal
        self.decreasing = decreasing

    def __call__(self, field, value):
        # can assume that len(value) == len(field.fields)
        last = None
        for v, f in map(None, value, field.fields):
            if v != f.missing_value:
                if last is not None:
                    if self.decreasing:
                        if self.may_be_equal:
                            if v > last:
                                raise MessageValidationError(
                                    _range_less_equal_error,
                                    {'minimum': v, 'maximum': last})
                        elif v >= last:
                            raise MessageValidationError(
                                _range_less_error,
                                {'minimum': v, 'maximum': last})
                    else:
                        if self.may_be_equal:
                            if v < last:
                                raise MessageValidationError(
                                    _range_less_equal_error,
                                    {'minimum': last, 'maximum': v})
                        elif v <= last:
                            raise MessageValidationError(
                                _range_less_error,
                                {'minimum': last, 'maximum': v})
                last = v
        

class Combination(BaseField):
    """a combination of two or more fields, all of which may be completed.
    
    It accepts two or more fields.  It also accepts a 'constraints' argument.
    Unlike the usual 'constraint' argument (which is also available), the
    constraints should be a sequence of callables that take a field and a
    value, and they should raise an error if there is a problem.
    
    >>> from zc.form.field import Combination, OrderedCombinationConstraint
    >>> from zope import schema, interface
    >>> class IDemo(interface.Interface):
    ...     publication_range = Combination(
    ...         (schema.Date(title=u'Begin', required=False),
    ...          schema.Date(title=u'Expire', required=True)),
    ...         title=u'Publication Range',
    ...         required=True,
    ...         constraints=(OrderedCombinationConstraint(),))
    ...
    >>> f = IDemo['publication_range']
    >>> interfaces.ICombinationField.providedBy(f)
    True
    >>> f.__name__
    'publication_range'
    >>> isinstance(f.fields[0], schema.Date)
    True
    >>> isinstance(f.fields[1], schema.Date)
    True
    >>> f.title
    u'Publication Range'
    >>> f.fields[0].title
    u'Begin'
    >>> f.fields[1].title
    u'Expire'
    >>> import datetime
    >>> f.validate((datetime.date(2005, 6, 22), datetime.date(2005, 7, 10)))
    >>> f.validate((None, datetime.date(2005, 7, 10)))
    >>> f.validate((datetime.date(2005, 6, 22), None))
    Traceback (most recent call last):
    ...
    RequiredMissing
    >>> f.validate(('foo', datetime.date(2005, 6, 22)))
    Traceback (most recent call last):
    ...
    WrongType: ('foo', <type 'datetime.date'>)
    >>> f.validate('foo') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    MessageValidationError: (u'The value has the wrong number of members', ...)
    >>> f.validate(17)
    Traceback (most recent call last):
    ...
    MessageValidationError: (u'The value is not a sequence', None)
    >>> f.validate((datetime.date(2005, 6, 22), datetime.date(1995, 7, 10)))
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    MessageValidationError: (u'${minimum} must be less than or equal to ...
    """

    interface.implements(interfaces.ICombinationField)

    fields = constraints = ()
    
    def __init__(self, fields, **kw):
        if len(fields) < 2:
            raise ValueError(_("combination must combine two or more fields"))
        for ix, field in enumerate(fields):
            if not IField.providedBy(field):
                raise DoesNotImplement(IField)
            field.__name__ = "combination_%02d" % ix
        self.fields = tuple(fields)
        super(Combination, self).__init__(**kw)

    def _validate(self, value):
        if value != self.missing_value:
            try:
                len_value = len(value)
            except (TypeError, AttributeError):
                raise MessageValidationError(
                    _combination_not_a_sequence_error)
            if len_value != len(self.fields):
                raise MessageValidationError(
                    _combination_wrong_size_error)
            for v, f in map(None, value, self.fields):
                f = f.bind(self.context)
                f.validate(v)
        super(Combination, self)._validate(value)

class QueryTextLineConstraint(BaseField, schema.TextLine):
    def __init__(self, index_getter=None, catalog_name=None, index_name=None):
        assert not ((catalog_name is None) ^ (index_name is None))
        assert (index_getter is None) ^ (catalog_name is None)
        self.catalog_name = catalog_name
        self.index_name = index_name
        self.index_getter = index_getter

    def __call__(self, field, value):
        if self.index_getter is not None:
            index = self.index_getter(self.context)
        else:
            catalog = component.getUtility(
                zope.app.catalog.interfaces.ICatalog,
                self.catalog_name,
                field.context)
            index = catalog[self.index_name]
        parser = zope.index.text.queryparser.QueryParser(index.lexicon)
        try:
            tree = parser.parseQuery(value)
        except zope.index.text.parsetree.ParseError, e:
            raise MessageValidationError(_bad_query)

class TextLine(BaseField, schema.TextLine):
    """An extended TextLine.

    >>> from zope.index.text.textindex import TextIndex
    >>> index = TextIndex()
    >>> class IDemo(interface.Interface):
    ...     query = TextLine(
    ...         constraints=(
    ...             QueryTextLineConstraint(
    ...                 lambda context: index),),
    ...         title=u"Text Query")
    ...
    >>> field = IDemo['query'].bind(None) # using None as context
    >>> field.validate(u'cow')
    >>> field.validate(u'cow and dog')
    >>> field.validate(u'a the') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    MessageValidationError: (u'Invalid query.', None)
    >>> field.validate(u'and') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    MessageValidationError: (u'Invalid query.', None)
    >>> field.validate(u'cow not dog')
    >>> field.validate(u'cow not not dog') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    MessageValidationError: (u'Invalid query.', None)
    >>> field.validate(u'cow and not dog')
    >>> field.validate(u'cow -dog')
    >>> field.validate('cow') # non-unicode fails, as usual with TextLine
    Traceback (most recent call last):
    ...
    WrongType: ('cow', <type 'unicode'>)
    """

class HTMLSnippet(BaseField, schema.Text):
    interface.implements(interfaces.IHTMLSnippet)

class HTMLDocument(BaseField, schema.Text):
    interface.implements(interfaces.IHTMLDocument)
