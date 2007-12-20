# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""References to persistent objects."""

import sys

import transaction
from persistent.dict import PersistentDict

import zope.app.container.interfaces
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


@zope.component.adapter(zope.interface.Interface,
                        zope.app.container.interfaces.IObjectMovedEvent)
def ensure_referential_integrity(obj, event):
    if event.oldParent is None:
        # The object was not in the hierarchy before so it didn't have a path
        # and can't be referenced currently.
        return

    # Compute the old path and watch out for the case that the object was
    # located in the root folder to avoid ending up with a double-slash in the
    # beginning.
    old_parent_path = zope.traversing.api.getPath(event.oldParent)
    if old_parent_path == '/':
        old_parent_path = ''
    old_path = (old_parent_path + '/' + event.oldName)

    manager = zope.component.getUtility(
        gocept.reference.interfaces.IReferenceManager)
    if manager.is_referenced(old_path):
        transaction.doom()
        raise gocept.reference.interfaces.IntegrityError(
            "Can't delete or move %r. It is still being referenced." % obj)


def find_references(obj):
    for name in dir(obj):
        attr = getattr(obj.__class__, name, None)
        if isinstance(attr, Reference):
            yield attr


@zope.component.adapter(zope.interface.Interface,
                        zope.app.container.interfaces.IObjectAddedEvent)
def ensure_registration(obj, event):
    for ref in find_references(obj):
        ref._register(obj)


@zope.component.adapter(zope.interface.Interface,
                        zope.app.container.interfaces.IObjectRemovedEvent)
def ensure_unregistration(obj, event):
    for ref in find_references(obj):
        ref._unregister(obj)


class Reference(object):
    """A descriptor for reference properties."""

    def __init__(self, __name__=None, ensure_integrity=False):
        self.__name__ = __name__
        self.ensure_integrity = ensure_integrity

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
        if value is None:
            self.storage(instance)[self.__name__] = None
            return
        target = zope.traversing.api.getPath(value)
        storage = self.storage(instance)
        self.storage(instance)[self.__name__] = target
        self._register(instance)

    @find_name
    def __delete__(self, instance):
        self._unregister(instance)
        del self.storage(instance)[self.__name__]

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
        except gocept.reference.interfaces.IntegrityError:
            # _register is called after data structures have been changed.
            transaction.doom()
            raise
        self.manager.register_reference(target_key)

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
            raise gocept.reference.interfaces.IntegrityError(
                "Target %r of reference %r no longer exists." %
                (target_key, self.__name__))
        return target
