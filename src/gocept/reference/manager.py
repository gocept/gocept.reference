# vim:fileencoding=utf-8
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Reference manager implementation."""

import persistent
import BTrees.OIBTree

import zope.interface
import zope.container.contained

import gocept.reference.interfaces


@zope.interface.implementer(gocept.reference.interfaces.IReferenceManager)
class ReferenceManager(persistent.Persistent,
                       zope.container.contained.Contained):

    def __init__(self):
        self.reference_count = BTrees.OIBTree.OIBTree()

    def register_reference(self, target, count=1):
        """Register a new reference to the given target."""
        if count == 0:
            return
        current = self.reference_count.get(target, 0)
        self.reference_count[target] = current + count

    def unregister_reference(self, target, count=1):
        """Register that a reference to the given target was removed."""
        if count == 0:
            return
        new = self.reference_count[target] - count
        if new == 0:
            del self.reference_count[target]
        else:
            self.reference_count[target] = new

    def is_referenced(self, target):
        """Tell whether the given target is being referenced."""
        return target in self.reference_count
