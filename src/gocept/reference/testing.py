# -*- coding: latin-1 -*-
# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest
import os.path
import zope.annotation.interfaces
import zope.app.container.contained
import zope.app.testing.functional
import zope.interface

import gocept.reference


ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = zope.app.testing.functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')


def FunctionalDocFileSuite(*paths, **kw):
    kw['optionflags'] = (kw.get('optionflags', 0) |
                         doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)
    suite = zope.app.testing.functional.FunctionalDocFileSuite(*paths, **kw)
    suite.layer = FunctionalLayer
    return suite


class Address(zope.app.container.contained.Contained):

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    city = gocept.reference.Reference()


class City(zope.app.container.contained.Contained):

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    cultural_institutions = gocept.reference.ReferenceCollection(
        ensure_integrity=True)


class Monument(zope.app.container.contained.Contained):

    zope.interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)

    city = gocept.reference.Reference(ensure_integrity=True)


class CulturalInstitution(zope.app.container.contained.Contained):
    title = None