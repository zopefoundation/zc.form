===============
Exception Views
===============

Convert an invariant error to an html snippet::

    >>> from zope.schema.interfaces import ValidationError
    >>> from zc.form.browser.exceptionviews import ValidationErrorView
    >>> err = ValidationError(
    ... "Bad error!  Bad!")
    >>> view = ValidationErrorView(err, None)
    >>> view.snippet()
    u'<span class="error">Bad error!  Bad!</span>'

This also works with unicode characters::

    >>> err = ValidationError(u"F\xe4lscher!")
    >>> view = ValidationErrorView(err, None)
    >>> view.snippet()
    u'<span class="error">F\xe4lscher!</span>'

HTML characters are quoted correctly::

    >>> err = ValidationError(u"The <error> & me.")
    >>> view = ValidationErrorView(err, None)
    >>> view.snippet()
    u'<span class="error">The &lt;error&gt; &amp; me.</span>'


The ConversionError has an exception as argument which is converted as well::

    >>> from zope.formlib.interfaces import ConversionError
    >>> err = ConversionError(ValidationError("not valid"))
    >>> view = ValidationErrorView(err, None)
    >>> view.snippet()
    u'<span class="error">not valid</span>'

