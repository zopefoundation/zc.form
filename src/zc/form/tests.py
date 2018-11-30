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
"""tests"""
import doctest


def test_suite():
    return doctest.DocTestSuite(
        "zc.form.field",
        optionflags=(doctest.NORMALIZE_WHITESPACE
                     | doctest.IGNORE_EXCEPTION_DETAIL
                     | doctest.REPORT_ONLY_FIRST_FAILURE
                     | doctest.ELLIPSIS
                     | doctest.REPORT_NDIFF),
    )
