# -*- coding: latin-1 -*-
import doctest
import os.path
import zope.annotation.interfaces
import zope.container.contained
import zope.app.testing.functional
import zope.interface

import gocept.reference


ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = zope.app.testing.functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')
FunctionalLayer.allow_teardown = True


def FunctionalDocFileSuite(*paths, **kw):
    kw['optionflags'] = (kw.get('optionflags', 0) |
                         doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)
    suite = zope.app.testing.functional.FunctionalDocFileSuite(*paths, **kw)
    suite.layer = FunctionalLayer
    return suite


@zope.interface.implementer(
        zope.annotation.interfaces.IAttributeAnnotatable)
class Address(zope.container.contained.Contained):

    city = gocept.reference.Reference()


@zope.interface.implementer(
        zope.annotation.interfaces.IAttributeAnnotatable)
class City(zope.container.contained.Contained):

    cultural_institutions = gocept.reference.ReferenceCollection(
        ensure_integrity=True)


@zope.interface.implementer(
        zope.annotation.interfaces.IAttributeAnnotatable)
class Village(zope.container.contained.Contained):

    cultural_institutions = gocept.reference.ReferenceCollection(
        ensure_integrity=False)


@zope.interface.implementer(
        zope.annotation.interfaces.IAttributeAnnotatable)
class Monument(zope.container.contained.Contained):

    city = gocept.reference.Reference(ensure_integrity=True)


class CulturalInstitution(zope.container.contained.Contained):
    title = None
