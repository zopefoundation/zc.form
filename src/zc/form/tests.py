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
"""tests

$Id: tests.py 621 2005-02-15 19:40:07Z jim $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.doctestunit import DocTestSuite

def test_suite():
    return TestSuite((
        DocTestSuite("zc.form.field"),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
