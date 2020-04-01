import gocept.reference.fix
import zope.component.hooks
import zope.generations.utility


def evolve(context):
    """Create usage counts of reference collections."""
    old_site = zope.component.hooks.getSite()
    root = zope.generations.utility.getRootFolder(context)
    try:
        zope.component.hooks.setSite(root)
        errors = gocept.reference.fix.Fixer().fix_reference_counts()
    finally:
        zope.component.hooks.setSite(old_site)
    if errors:
        print('The following errors were encountered while trying to update '
              'gocept.reference reference counts:')
        for key, name, msg in errors:
            print('<%s>.%s: %s' % (key, name, msg))
