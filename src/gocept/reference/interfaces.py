# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interface specifications for gocept.reference."""


import zope.interface


class IntegrityError(Exception):
    pass


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
