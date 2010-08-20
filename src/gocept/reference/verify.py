# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface.verify
import zope.interface.exceptions

import gocept.reference.reference
import gocept.reference.collection


def verifyObject(iface, candidate, tentative=0):
    "Specialized variant of verifyObject which handles references correctily."
    class_ = candidate.__class__
    # zope.interface.verify.verifyClass returns True or raises exception
    zope.interface.verify.verifyClass(iface, class_, tentative=tentative)
    for name, desc in iface.namesAndDescriptions(1):
        if hasattr(candidate, name):
            continue
        # if instance does not provide attribute, look on class if it
        # has a reference or reference collection, as both may raise
        # an AttributeError when checked on instance.
        if hasattr(class_, name):
            attr = getattr(class_, name)
            if (isinstance(attr, gocept.reference.reference.Reference) or
                isinstance(
                    attr, gocept.reference.collection.ReferenceCollection)):
                continue
        raise zope.interface.exceptions.BrokenImplementation(iface, name)
    return True
