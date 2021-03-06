# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Install the reference package."""

import gocept.reference.interfaces
import gocept.reference.manager
import zope.generations.utility


def evolve(context):
    # Install the reference manager utility into the root site.
    root = zope.generations.utility.getRootFolder(context)
    sm = root.getSiteManager()
    if 'gocept.reference' not in sm:
        sm['gocept.reference'] = gocept.reference.manager.ReferenceManager()
        sm.registerUtility(
            sm['gocept.reference'],
            provided=gocept.reference.interfaces.IReferenceManager)
