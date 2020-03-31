# vim:fileencoding=utf-8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""References to persistent objects."""

import transaction
from persistent.dict import PersistentDict

import zope.component.hooks
import zope.annotation.interfaces
import zope.traversing.interfaces
import zope.traversing.api

import gocept.reference.interfaces
import six


def find_name(method):
    """Tries to determine the name of the property in the instance's
    class.

    The result is cached during the runtime of the process.

    """
    def descriptor_name_by_inspection(descriptor, instance, *args):
        if instance is None:
            # We're called via __get__ on a class. In this case, the class is
            # passed as the next argument after the instance.
            cls = args[0]
        else:
            cls = instance.__class__
        # We cannot simply iterate over dir(cls) since trying to get the
        # attributes would then lead to infinite recursion.
        for cls_ in cls.mro():
            for name, attr in six.iteritems(cls_.__dict__):
                if attr is descriptor:
                    return name
        else:
            raise RuntimeError(  # pragma: no cover
                "Can not automatically find name for reference. "
                "This place in the code should never be reached.")

    def wrapper(self, instance, *args):
        if not self.__name__:
            self.__name__ = descriptor_name_by_inspection(
                self, instance, *args)
        return method(self, instance, *args)

    return wrapper


def get_manager():
    return zope.component.getUtility(
        gocept.reference.interfaces.IReferenceManager)


def get_root():
    site = zope.component.hooks.getSite()
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

    def __init__(self, __name__=None, ensure_integrity=False):
        self.__name__ = __name__
        self.ensure_integrity = ensure_integrity

    @find_name
    def __delete__(self, instance):
        self._unregister(instance)
        del get_storage(instance)[self.__name__]

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

    @find_name
    def __set__(self, instance, value):
        self._unregister(instance)
        storage = get_storage(instance)
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
        target_key = get_storage(instance).get(self.__name__)
        if not target_key:
            return
        get_manager().unregister_reference(target_key)

    def _register(self, instance):
        if not self.needs_registration(instance):
            return
        target_key = get_storage(instance).get(self.__name__)
        if target_key is None:
            # The reference source is being put under integrity ensurance but
            # this reference has not yet been set.
            return
        try:
            lookup(target_key)
        except gocept.reference.interfaces.LookupError:
            # _register is called after data structures have been changed.
            transaction.doom()
            raise
        get_manager().register_reference(target_key)
