# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.reference.collection
import gocept.reference.content
import gocept.reference.reference
import zope.traversing.api


class Fixer(object):
    """Tool for restoring consistent reference counts.

    path: path to the location to work in

    """

    def __init__(self):
        self.root = gocept.reference.reference.lookup(u'/')

    def reset_all_counts(self):
        manager = gocept.reference.reference.get_manager()
        manager.reference_count.clear()
        for obj in gocept.reference.content.sublocation_tree(self.root):
            for name, ref in gocept.reference.content.find_references(obj):
                if isinstance(
                        ref, gocept.reference.collection.ReferenceCollection):
                    iset = getattr(obj, name, None)
                    if iset is not None:
                        iset._ensured_usage_count = 0

    def fix_reference_counts(self):
        """Fix reference counts.

        If errors are encountered, returns a list of references concerned.

        """
        self.reset_all_counts()
        errors = []
        for obj in gocept.reference.content.sublocation_tree(self.root):
            for name, ref in gocept.reference.content.find_references(obj):
                try:
                    ref._register(obj)
                except Exception, e:
                    key = zope.traversing.api.getPath(obj)
                    errors.append((key, name, str(e)))
        return errors
