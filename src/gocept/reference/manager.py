# vim:fileencoding=utf-8
# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Reference manager implementation."""

import persistent
import BTrees.OIBTree

import zope.interface
import zope.container.contained

import gocept.reference.interfaces


class ReferenceManager(persistent.Persistent,
                       zope.container.contained.Contained):

    zope.interface.implements(gocept.reference.interfaces.IReferenceManager)

    def __init__(self):
        self.reference_count = BTrees.OIBTree.OIBTree()

    def register_reference(self, target):
        """Register a new reference to the given target."""
        current = self.reference_count.get(target, 0)
        self.reference_count[target] = current + 1

    def unregister_reference(self, target):
        """Register that a reference to the given target was removed."""
        new = self.reference_count[target] - 1
        if new == 0:
            del self.reference_count[target]
        else:
            self.reference_count[target] = new

    def is_referenced(self, target):
        """Tell whether the given target is being referenced."""
        return target in self.reference_count
