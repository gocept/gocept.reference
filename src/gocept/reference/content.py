# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interaction between the reference machinery and content objects."""

import zope.interface
import zope.component
import zope.traversing.interfaces

import gocept.reference.interfaces
import gocept.reference.reference


class ReferenceSource(object):

    zope.interface.implements(gocept.reference.interfaces.IReferenceSource)
    zope.component.adapts(zope.interface.Interface)

    def __init__(self, context):
        self.context = context

    def verify_integrity(self):
        for name, ref in gocept.reference.reference.find_references(
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
