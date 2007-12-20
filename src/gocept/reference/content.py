# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interaction between the reference machinery and content objects."""

import transaction

import zope.interface
import zope.component
import zope.traversing.interfaces
import zope.traversing.api
import zope.app.container.interfaces

import gocept.reference.interfaces
import gocept.reference.reference


def find_references(obj):
    for name in dir(obj):
        attr = getattr(obj.__class__, name, None)
        if isinstance(attr, gocept.reference.reference.Reference):
            yield name, attr


class ReferenceSource(object):

    zope.interface.implements(gocept.reference.interfaces.IReferenceSource)
    zope.component.adapts(zope.interface.Interface)

    def __init__(self, context):
        self.context = context

    def verify_integrity(self):
        for name, ref in find_references(
            self.context):
            target_key = ref.storage(self.context).get(name)
            if target_key:
                try:
                    ref.lookup(target_key)
                except gocept.reference.interfaces.IntegrityError:
                    return False
        return True


class ReferenceTarget(object):

    zope.interface.implements(gocept.reference.interfaces.IReferenceTarget)
    zope.component.adapts(zope.interface.Interface)

    def __init__(self, context):
        self.context = context

    def is_referenced(self):
        manager = zope.component.getUtility(
            gocept.reference.interfaces.IReferenceManager)
        locatable = zope.traversing.interfaces.IPhysicallyLocatable(
                self.context)
        return manager.is_referenced(locatable.getPath())


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


@zope.component.adapter(zope.interface.Interface,
                        zope.app.container.interfaces.IObjectAddedEvent)
def ensure_registration(obj, event):
    for name, ref in find_references(obj):
        if ref.storage(obj).get(name):
            ref._register(obj)


@zope.component.adapter(zope.interface.Interface,
                        zope.app.container.interfaces.IObjectRemovedEvent)
def ensure_unregistration(obj, event):
    for name, ref in find_references(obj):
        ref._unregister(obj)
