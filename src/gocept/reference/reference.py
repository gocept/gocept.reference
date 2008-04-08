# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""References to persistent objects."""

import transaction
from persistent.dict import PersistentDict

import zope.app.component.hooks
import zope.annotation.interfaces
import zope.traversing.interfaces
import zope.traversing.api

import gocept.reference.interfaces


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


class ReferenceBase(object):
    """A base class for specific references."""

    def __init__(self, __name__=None, ensure_integrity=False):
        self.__name__ = __name__
        self.ensure_integrity = ensure_integrity

    @find_name
    def __delete__(self, instance):
        self._unregister(instance)
        del self.storage(instance)[self.__name__]

    @property
    def manager(self):
        return zope.component.getUtility(
            gocept.reference.interfaces.IReferenceManager)

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

    def needs_registration(self, instance):
        if not self.ensure_integrity:
            return False
        try:
            zope.traversing.interfaces.IPhysicallyLocatable(instance
                                                            ).getPath()
        except TypeError:
            return False

        return True

    def lookup(self, target_key):
        try:
            target = zope.traversing.api.traverse(self.root, target_key)
        except zope.traversing.interfaces.TraversalError:
            raise gocept.reference.interfaces.LookupError(target_key, self)
        return target


class Reference(ReferenceBase):
    """A descriptor for reference properties."""

    @find_name
    def __get__(self, instance, owner):
        if instance is None:
            return self

        try:
            target_key = self.storage(instance)[self.__name__]
        except KeyError:
            raise AttributeError(self.__name__)
        if target_key is None:
            return None
        return self.lookup(target_key)

    @find_name
    def __set__(self, instance, value):
        self._unregister(instance)
        storage = self.storage(instance)
        if value is None:
            storage[self.__name__] = None
            return
        target = zope.traversing.api.getPath(value)
        storage[self.__name__] = target
        self._register(instance)

    # Helper methods

    def _unregister(self, instance):
        if not self.needs_registration(instance):
            return
        target_key = self.storage(instance).get(self.__name__)
        if not target_key:
            return
        self.manager.unregister_reference(target_key)

    def _register(self, instance):
        if not self.needs_registration(instance):
            return
        target_key = self.storage(instance)[self.__name__]
        try:
            self.lookup(target_key)
        except gocept.reference.interfaces.LookupError:
            # _register is called after data structures have been changed.
            transaction.doom()
            raise
        self.manager.register_reference(target_key)
