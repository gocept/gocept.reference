# -*- coding: latin-1 -*-
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
""" XXX """

import unittest
import doctest
import os.path

from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer


ftesting_zcml = os.path.join(
    os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')


def test_suite():
    suite = FunctionalDocFileSuite('reference.txt',
                                   optionflags=doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
