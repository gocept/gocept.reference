# vim:fileencoding=utf-8
# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""References to persistent objects."""

import transaction
from persistent.dict import PersistentDict

import zope.site.hooks
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


def get_manager():
    return zope.component.getUtility(
        gocept.reference.interfaces.IReferenceManager)


def get_root():
    site = zope.site.hooks.getSite()
    locatable = zope.traversing.interfaces.IPhysicallyLocatable(site)
    return locatable.getRoot()


def lookup(target_key):
    try:
        target = zope.traversing.api.traverse(get_root(), target_key)
    except zope.traversing.interfaces.TraversalError:
        raise gocept.reference.interfaces.LookupError(target_key)
    return target


def get_storage(instance):
    annotations = zope.annotation.interfaces.IAnnotations(instance)
    result = annotations.get('gocept.reference')
    if result is None:
        result = annotations['gocept.reference'] = PersistentDict()
    return result


class ReferenceBase(object):
    """A base class for specific references."""

    def __init__(self, __name__=None, ensure_integrity=False,
                 back_reference=None):
        self.__name__ = __name__
        self.ensure_integrity = ensure_integrity
        self.back_reference = back_reference

    @find_name
    def __delete__(self, instance):
        self._unregister(instance)
        del get_storage(instance)[self.__name__]

    @find_name
    def name(self):
        return self.__name__

    def needs_registration(self, instance):
        if not self.ensure_integrity:
            return False
        try:
            zope.traversing.interfaces.IPhysicallyLocatable(instance
                                                            ).getPath()
        except TypeError:
            return False

        return True


class Reference(ReferenceBase):
    """A descriptor for reference properties."""

    @find_name
    def __get__(self, instance, owner):
        if instance is None:
            return self

        try:
            target_key = get_storage(instance)[self.__name__]
        except KeyError:
            raise AttributeError(self.__name__)
        if target_key is None:
            return None
        return lookup(target_key)

    def __set__(self, instance, value):
        self.reference(instance, value)
        if self.back_reference and value is not None:
            other = get_manager().lookup_backreference(
                value, self.back_reference)
            other.reference(value, instance)

    @find_name
    def reference(self, instance, target):
        if self.back_reference:
            self._clear_backref(instance)

        self._unregister(instance)
        storage = get_storage(instance)
        if target is None:
            storage[self.__name__] = None
            return
        target = zope.traversing.api.getPath(target)
        storage[self.__name__] = target
        self._register(instance)

    @find_name
    def unreference(self, instance, target):
        self._unregister(instance)
        storage = get_storage(instance)
        storage[self.__name__] = None

    # Helper methods

    def _unregister(self, instance):
        if not self.needs_registration(instance):
            return
        target_key = get_storage(instance).get(self.__name__)
        if not target_key:
            return
        get_manager().unregister_reference(target_key)

    def _register(self, instance):
        if not self.needs_registration(instance):
            return
        target_key = get_storage(instance)[self.__name__]
        try:
            lookup(target_key)
        except gocept.reference.interfaces.LookupError:
            # _register is called after data structures have been changed.
            transaction.doom()
            raise
        get_manager().register_reference(target_key)

    def _clear_backref(self, instance):
        target = getattr(instance, self.__name__, None)
        if target is None:
            return
        other = get_manager().lookup_backreference(
            target, self.back_reference)
        other.unreference(target, instance)
