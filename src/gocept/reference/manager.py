# vim:fileencoding=utf-8
# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Reference manager implementation."""

import persistent
import BTrees.OIBTree

import zope.interface 
import zope.app.container.contained

import gocept.reference.interfaces
import gocept.reference.reference


class ReferenceManager(persistent.Persistent,
                       zope.app.container.contained.Contained):

    zope.interface.implements(gocept.reference.interfaces.IReferenceManager)

    def __init__(self):
        self.reference_count = BTrees.OIBTree.OIBTree()
        self.backreference_cache = {} # don't store class-related information
                                      # persistently

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

    def lookup_backreference(self, target, ref_name):
        # Look up the attribute in the cache first.
        attrs = self.backreference_cache.setdefault(ref_name, {})
        attr = attrs.get(target.__class__)
        if attr:
            return attr

        # Wasn't in the cache, so search for it. Search the whole class dict
        # in order to guard against ambiguities.
        for candidate in target.__class__.__dict__.itervalues():
            if (isinstance(candidate,
                           gocept.reference.reference.ReferenceBase) and
                candidate.back_reference == ref_name):
                if attr:
                    raise LookupError(
                        'Ambiguous back reference %r from %r.' %
                        (ref_name, target.__class__))
                attr = candidate

        if not attr:
            raise LookupError('No back reference %r from %r.' %
                              (ref_name, target.__class__))

        # Cache and return the result after no ambiguities have been found.
        attrs[target.__class__] = attr
        return attr
