# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Install the reference package."""

import zope.app.zopeappgenerations

import gocept.reference.manager
import gocept.reference.interfaces


def evolve(context):
    # Install the reference manager utility into the root site.
    root = zope.app.zopeappgenerations.getRootFolder(context)
    sm = root.getSiteManager()
    sm['gocept.reference'] = gocept.reference.manager.ReferenceManager()
    sm.registerUtility(sm['gocept.reference'],
                       provided=gocept.reference.interfaces.IReferenceManager)
