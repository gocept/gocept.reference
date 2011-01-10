# -*- coding: latin-1 -*-
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
""" XXX """

import unittest
import doctest
import os.path

import zope.interface
import zope.annotation.interfaces
from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer
from zope.app.container.contained import Contained

import gocept.reference


class Address(Contained):

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    city = gocept.reference.Reference()


class City(Contained):

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    cultural_institutions = gocept.reference.ReferenceCollection(
        ensure_integrity=True)


class Monument(Contained):

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    city = gocept.reference.Reference(ensure_integrity=True)


class CulturalInstitution(Contained):
    title = None

ftesting_zcml = os.path.join(
    os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')


def test_suite():
    suite = FunctionalDocFileSuite(
      'reference.txt',
      'collection.txt',
      'verify.txt',
      optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    suite.layer = FunctionalLayer
    return suite
