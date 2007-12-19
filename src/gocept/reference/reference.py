# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""References to persistent objects."""

import sys

from persistent.dict import PersistentDict

import zope.app.component.hooks
import zope.annotation.interfaces
import zope.traversing.interfaces

import z3c.objpath


def find_name(method):
    """Tries to determine the name of the property in the instance's 
    class.

    The result is cached during the runtime of the process.

    """

    def find_name_impl(self, instance, *args, **kw):
        if not self.__name__:
            for name, attr in instance.__class__.__dict__.items():
                if self is attr:
                    self.__name__ = name
                    break
            else:
                raise AttributeError(
                    "Can not automatically find name for reference. "
                    "Please use the __name__ parameter.")
        return method(self, instance, *args, **kw)
    return find_name_impl


class Reference(object):
    """A descriptor for reference properties."""

    def __init__(self, __name__=None):
        self.__name__ = __name__

    def __get__(self, instance, owner):
        target = self.storage(instance)[self.__name__]
        return z3c.objpath.resolve(self.root, target)

    def __set__(self, instance, value):
        target = z3c.objpath.path(self.root, value)
        self.storage(instance)[self.__name__] = target

    def __delete__(self, instance):
        del self.storage(instance)[self.__name__]

    @property
    def root(self):
        site = zope.app.component.hooks.getSite()
        locatable = zope.traversing.interfaces.IPhysicallyLocatable(site)
        return locatable.getRoot()

    def storage(self, instance):
        annotations = zope.annotation.interfaces.IAnnotations(instance)
        result = annotations.get('gocept.reference')
        if result is None:
            result = annotations['gocept.reference'] = PersistentDict()
        return result
