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
"""I18N support for the form package.

This defines a `MessageFactory` for the I18N domain for the zc.form
package.  This is normally used with this import::

  from i18n import MessageFactory as _

The factory is then used normally.  Two examples::

  text = _('some internationalized text')
  text = _('helpful-descriptive-message-id', 'default text')
"""
__docformat__ = "reStructuredText"


from zope import i18nmessageid

MessageFactory = _ = i18nmessageid.MessageFactory("zc.form")
