# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interface specifications for gocept.reference."""


import zope.interface


class IntegrityError(Exception):
    pass


class IReferenceManager(zope.interface.Interface):
    """Utility for managing references."""

    def register_reference(target):
        """Register a new reference to the given target."""

    def unregister_reference(target):
        """Register that a reference to the given target was removed."""

    def is_referenced(target):
        """Tell whether the given target is being referenced."""
