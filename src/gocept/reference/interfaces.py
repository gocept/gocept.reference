# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interface specifications for gocept.reference."""


import zope.interface


class IntegrityError(Exception):

    def __init__(self, to_delete, referenced):
        self.to_delete = to_delete
        self.referenced = referenced

    def __str__(self):
        return ("Can't delete or move %r. The (sub-)object %r is still being "
                "referenced." % (self.to_delete, self.referenced))


class LookupError(KeyError):

    def __init__(self, target_key, reference):
        self.target_key = target_key
        self.reference = reference

    def __str__(self):
        return "Target %r of reference %r no longer exists." % (
            self.target_key, self.reference.__name__)


class IReferenceSource(zope.interface.Interface):
    """Interact with an object that holds references."""

    def verify_integrity():
        """Tell whether referential integrity is given."""


class IReferenceTarget(zope.interface.Interface):
    """Interact with an object that may be referenced."""

    def is_referenced():
        """Tell whether any references to the object exist."""


class IReferenceManager(zope.interface.Interface):
    """Utility for managing references."""

    def register_reference(target):
        """Register a new reference to the given target."""

    def unregister_reference(target):
        """Register that a reference to the given target was removed."""

    def is_referenced(target):
        """Tell whether the given target is being referenced."""
