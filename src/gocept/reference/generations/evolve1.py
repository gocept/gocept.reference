# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.reference.fix


def evolve(context):
    """Create usage counts of reference collections."""
    errors = gocept.reference.fix.Fixer().fix_reference_counts()
    if errors:
        print ('The following errors were encountered while trying to update '
               'gocept.reference reference counts:')
        for key, name, msg in errors:
            print '<%s>.%s: %s' % (key, name, msg)
