# vim:fileencoding=utf-8
"""Interaction between the reference machinery and content objects."""

import transaction

import zope.interface
import zope.component
import zope.location
import zope.traversing.interfaces
import zope.traversing.api
import zope.container.interfaces

import gocept.reference.interfaces
import gocept.reference.reference


def find_references(obj):
    for name in dir(obj.__class__):
        attr = getattr(obj.__class__, name, None)
        if isinstance(attr, gocept.reference.reference.ReferenceBase):
            yield name, attr


def sublocation_tree(obj):
    yield obj
    isub = zope.location.interfaces.ISublocations(obj, None)
    if isub:
        for direct in isub.sublocations():
            for sub in sublocation_tree(direct):
                yield sub


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(gocept.reference.interfaces.IReferenceSource)
class ReferenceSource(object):

    def __init__(self, context):
        self.context = context

    def verify_integrity(self):
        for name, ref in find_references(
                self.context):
            target_key = gocept.reference.reference.get_storage(
                self.context).get(name)
            if target_key:
                try:
                    gocept.reference.reference.lookup(target_key)
                except gocept.reference.interfaces.LookupError:
                    return False
        return True


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(gocept.reference.interfaces.IReferenceTarget)
class ReferenceTarget(object):

    def __init__(self, context):
        self.context = context

    def is_referenced(self, recursive=True):
        if recursive:
            candidates = sublocation_tree(self.context)
        else:
            candidates = [self.context]
        manager = zope.component.getUtility(
            gocept.reference.interfaces.IReferenceManager)
        for obj in candidates:
            locatable = zope.traversing.interfaces.IPhysicallyLocatable(obj)
            if manager.is_referenced(locatable.getPath()):
                return True
        else:
            return False


@zope.component.adapter(zope.interface.Interface,
                        zope.container.interfaces.IObjectMovedEvent)
def ensure_referential_integrity(obj, event):
    if event.oldParent is None:
        # The object was not in the hierarchy before so it didn't have a path
        # and can't be referenced currently.
        return

    # 1. Compute the old path to the container that an object was removed from
    old_parent_path = zope.traversing.api.getPath(event.oldParent)
    if old_parent_path == '/':
        # The object that was removed was located in the root folder. We
        # remove the slash to avoid ending up with a double-slash in the next
        # step.
        old_parent_path = ''

    # 2. Compute the path to the object that was removed
    old_path = (old_parent_path + '/' + event.oldName)

    # 3. If our obj is not the moved object then we're a sublocation and need
    # to reconstruct the further path to the sublocation.
    suffix = ''
    suffix_obj = obj
    while suffix_obj is not event.object:
        suffix = '/%s%s' % (suffix_obj.__name__, suffix)
        suffix_obj = suffix_obj.__parent__
    old_path = old_path + suffix

    manager = zope.component.getUtility(
        gocept.reference.interfaces.IReferenceManager)
    if manager.is_referenced(old_path):
        transaction.doom()
        raise gocept.reference.interfaces.IntegrityError(event.object, obj)


@zope.component.adapter(zope.interface.Interface,
                        zope.container.interfaces.IObjectAddedEvent)
def ensure_registration(obj, event):
    for name, ref in find_references(obj):
        ref._register(obj)


@zope.component.adapter(zope.interface.Interface,
                        zope.container.interfaces.IObjectRemovedEvent)
def ensure_unregistration(obj, event):
    for name, ref in find_references(obj):
        ref._unregister(obj)
