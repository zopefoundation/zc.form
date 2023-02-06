=======
Changes
=======

2.0 (2023-02-06)
----------------

- Add support for Python 3.8, 3.9, 3.10, 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


1.1 (2019-02-11)
----------------

- Fix ZCML configuration issue if the ``[mruwidget]`` extra was not installed.


1.0 (2019-01-11)
----------------

Features
++++++++

- Claim support for Python 3.5, 3.6, 3.7, PyPy and PyPy3.

Bugfixes
++++++++

- Fix a ``NameError`` in ``BaseVocabularyDisplay.render()``.

- Actually pass a ``missing_value`` set on the ``Combination`` field to the
  containing fields.

Caveats
+++++++

- Installation of ``MruSourceInputWidget`` and ``TimeZoneWidget`` requires the
  ``[mruwidget]`` extra to break dependency on ``zc.resourcelibrary`` for
  projects which do not need it.


0.5 (2016-08-02)
----------------

- Bind fields that are contained in a ``zc.form.field.Combination`` to fix the
  ``context`` of those fields.


0.4 (2016-01-12)
----------------

- Get rid of the `zope.app.pagetemplate` dependency.


0.3 (2014-04-23)
----------------

- Remove requirement, that ``zc.form.field.Combination`` needs at least
  two subfields.


0.2 (2011-09-24)
----------------

- Got rid of ``zope.app.form`` dependency by requiring at least
  ``zope.formlib`` 4.0.

- Got rid of ``zope.app.component`` dependency by requiring at least
  ``zope.component`` 3.8.

- Depending on ``zope.catalog`` instead of ``zope.app.catalog``.

- Depending on ``zope.security`` instead of ``zope.app.security``.

- Depending on ``zope.app.wsgi`` >=3.7 instead of ``zope.app.testing`` for
  test setup.

- Depending on ``zope.browserpage`` and ``zope.container`` instead of
  ``zope.app.publisher``.

- Got rid of the following dependencies:

  - ``zope.app.basicskin``
  - ``zope.app.securitypolicy``
  - ``zope.app.zapi``
  - ``zope.app.zcmlfiles``

- Fixed tests to run with ``zope.schema`` >= 3.6.

- Made package fit to run on ZTK 1.1.

- Moved test dependencies to `test` extra.

- Using Python's ``doctest`` module instead of deprecated
  ``zope.testing.doctest``.


0.1
---

- Exception views are now unicode aware. They used to break on translated
  content.

- Added use_default_for_not_selected to Union field to use default
  value even if sub field is not selected.
