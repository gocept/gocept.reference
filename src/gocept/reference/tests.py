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

    city = gocept.reference.Reference()

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    def __init__(self, name, city):
        self.name = name
        self.city = city


class City(Contained):

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    cultural_institutions = gocept.reference.ReferenceCollection(
        ensure_integrity=True)

    def __init__(self, name, zip):
        self.name = name
        self.zip = zip


class Monument(Contained):

    city = gocept.reference.Reference(ensure_integrity=True)

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    def __init__(self, name, city):
        self.name = name
        self.city = city


class CulturalInstitution(Contained):

    def __init__(self, title):
      self.title = title


ftesting_zcml = os.path.join(
    os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')


def test_suite():
    suite = FunctionalDocFileSuite(
      'reference.txt',
      'collection.txt',
      optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    suite.layer = FunctionalLayer
    return suite
