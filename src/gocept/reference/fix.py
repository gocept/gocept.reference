import gocept.reference.collection
import gocept.reference.content
import gocept.reference.reference
import sys
import transaction
import zope.traversing.api


class Fixer(object):
    """Tool for restoring consistent reference counts.

    The __init__ takes the following arguments:

    do_savepoints: commit a savepoint every `savepoint_step` (default: False)
    savepoint_step: when a savepoint is committed or logged (default: 5000)
    verbose: print some progress to standard out (default: False)
    """

    do_savepoints = None
    savepoint_step = None
    verbose = False

    def __init__(
            self, do_savepoints=False, savepoint_step=5000, verbose=False):
        self.root = gocept.reference.reference.lookup(u'/')
        self.do_savepoints = do_savepoints
        self.savepoint_step = savepoint_step
        self.verbose = verbose

    def reset_all_counts(self):
        manager = gocept.reference.reference.get_manager()
        manager.reference_count.clear()
        obj_count = 0
        for obj in gocept.reference.content.sublocation_tree(self.root):
            for name, ref in gocept.reference.content.find_references(obj):
                if isinstance(
                        ref, gocept.reference.collection.ReferenceCollection):
                    iset = getattr(obj, name, None)
                    if iset is not None:
                        iset._ensured_usage_count = 0
            obj_count += 1
            if obj_count % self.savepoint_step == 0:
                if self.verbose:
                    print('{} objects reseted.'.format(obj_count))
                    sys.stdout.flush()
                if self.do_savepoints:
                    transaction.savepoint()

    def fix_reference_counts(self):
        """Fix reference counts.

        If errors are encountered, returns a list of references concerned.

        """
        self.reset_all_counts()
        errors = []
        obj_count = 0
        for obj in gocept.reference.content.sublocation_tree(self.root):
            for name, ref in gocept.reference.content.find_references(obj):
                try:
                    ref._register(obj)
                except Exception as e:
                    key = zope.traversing.api.getPath(obj)
                    errors.append((key, name, str(e)))
            obj_count += 1
            if obj_count % self.savepoint_step == 0:
                if self.verbose:
                    print('{} objects registered.'.format(obj_count))
                    sys.stdout.flush()
                if self.do_savepoints:
                    transaction.savepoint()

        return errors
