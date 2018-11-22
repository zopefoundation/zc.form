========================================
 Most Recently Used (MRU) Source Widget
========================================

The MRU widget keeps track of the last few values selected (on a per-principal
basis) and allows quickly selecting from that list instead of using a query
interface.

We can see the widget in action by using a custom form.  Let's define a schema
for the form that uses a source::

    >>> import zope.interface
    >>> import zope.schema

    >>> class IDemo(zope.interface.Interface):
    ...
    ...     color = zope.schema.Choice(
    ...         title=u"Color",
    ...         description=u"My favorite color",
    ...         source=AvailableColors,
    ...         )

And then a class that implements the interface::

    >>> class Demo(object):
    ...     zope.interface.implements(IDemo)
    ...
    ...     color = None

We'll need a form that uses this schema::

    >>> import zope.formlib.form

    >>> class DemoInput(zope.formlib.form.EditForm):
    ...     actions = ()
    ...     form_fields = zope.formlib.form.fields(IDemo)

By rendering the form we can see that there are no MRU items to choose from
(because this principal has never visited this form before) and the query
interface is displayed::

    >>> import zope.publisher.browser
    >>> import zope.security.interfaces
    >>> import zope.security.management
    >>> import zope.component.hooks

    >>> class DummyPrincipal(object):
    ...     zope.interface.implements(zope.security.interfaces.IPrincipal)
    ...
    ...     id = "someuser"
    ...     title = "Some User's Name"
    ...     description = "A User"

Note that we need to use the special resourcelibrary request.  We're
hacking together the TestRequest and the resourcelibrary request here; when we
switch to TestBrowser we can remove this oddity.

    >>> import zc.resourcelibrary.publication
    >>> class TestRequest(zope.publisher.browser.TestRequest,
    ...                   zc.resourcelibrary.publication.Request):
    ...     def _createResponse(self):
    ...         return zc.resourcelibrary.publication.Request._createResponse(
    ...             self)
    ...

    >>> request = TestRequest()
    >>> principal = DummyPrincipal()
    >>> request.setPrincipal(principal)
    >>> zope.security.management.newInteraction(request)

    >>> oldsite = zope.component.hooks.getSite()
    >>> zope.component.hooks.setSite(getRootFolder())

Now we can use an instance of our demo object to see that the form
pulls the possible values from the vocabulary we've defined above::

    >>> form = DemoInput(Demo(), request)
    >>> print form()
    <...
    <div class="queries"...>
    <div class="query"...>
      <div class="queryinput"...>
        <query view for colors>
      </div> <!-- queryinput -->
    </div> <!-- query -->
    </div> <!-- queries -->
    ...

Note that the select box of MRU values isn't in the output, because the user
has never selected a value before::

    >>> '<select name="form.color">' not in form()
    True

Now, we can select one of the values::

    >>> zope.security.management.endInteraction()

    >>> request = TestRequest()
    >>> request.form = {
    ...     'form.color.query.selection': 'red_token',
    ...     'form.color.query.apply': 'Apply',
    ...     'form.color.displayed': '',
    ...     }
    >>> request.setPrincipal(principal)

    >>> zope.security.management.newInteraction(request)

Process the request and the list of MRU values is in the form::

    >>> form = DemoInput(Demo(), request)
    >>> print form()
    <...
    <select name="form.color" id="form.color">
      <option value="red_token" selected="selected">Red</option>
    </select>
    ...

And the query view is hidden because we have an MRU list::

    >>> print form()
    <...
    <input type="hidden" name="form.color.queries.visible" ... value="no">
    ...

If we select another value...::

    >>> request = TestRequest()
    >>> request.form = {
    ...     'form.color.query.selection': 'green_token',
    ...     'form.color.query.apply': 'Apply',
    ...     'form.color.displayed': '',
    ...     }
    >>> request.setPrincipal(principal)

...and process the request, the list of MRU values includes the new one, at
the top, and it is selected::

    >>> form = DemoInput(Demo(), request)
    >>> print form()
    <...
    <select name="form.color" id="form.color">
      <option value="green_token" selected="selected">Green</option>
      <option value="red_token">Red</option>
    </select>
    ...

Clean up a bit::

    >>> zope.security.management.endInteraction()
    >>> zope.component.hooks.setSite(oldsite)
