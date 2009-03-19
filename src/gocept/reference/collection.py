# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Reference lists."""

import sets

import BTrees.OOBTree
import persistent
import transaction
import zope.component
import zope.container.interfaces
import zope.interface
import zope.traversing.api

import gocept.reference.reference


class ReferenceCollection(gocept.reference.reference.ReferenceBase):
    """A descriptor for lists of references."""

    @gocept.reference.reference.find_name
    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            target_set = gocept.reference.reference.get_storage(
                instance)[self.__name__]
        except KeyError:
            raise AttributeError(self.__name__)
        return target_set

    @gocept.reference.reference.find_name
    def __set__(self, instance, value):
        if isinstance(value, (set, sets.BaseSet)):
            value = InstrumentedSet(value)
        if value is not None and not isinstance(value, InstrumentedSet):
            raise TypeError("%r can't be assigned as a reference collection: "
                            "only sets are allowed." % value)
        self._unregister(instance)
        storage = gocept.reference.reference.get_storage(instance)
        if storage.get(self.__name__) is not None:
            storage[self.__name__].discard_usage(
                instance, self.name(instance))
        storage[self.__name__] = value
        if value is not None:
            value.add_usage(instance, self.name(instance))
            self._register(instance)

    def reference(self, instance, target):
        getattr(instance, self.__name__).reference(target)

    def unreference(self, instance, target):
        getattr(instance, self.__name__).unreference(target)

    def _unregister(self, instance):
        if not self.needs_registration(instance):
            return
        target_set = gocept.reference.reference.get_storage(
            instance).get(self.__name__)
        if not target_set:
            return
        target_set._unregister_all()

    def _register(self, instance):
        if not self.needs_registration(instance):
            return
        target_set = gocept.reference.reference.get_storage(
            instance).get(self.__name__)
        if target_set is None:
            return
        target_set._register_all()


class InstrumentedSet(persistent.Persistent):

    def __init__(self, src):
        # Convert objects to their keys
        self._data = BTrees.OOBTree.TreeSet(
            zope.traversing.api.getPath(item) for item in src)
        self._usage = BTrees.OOBTree.OOBTree()

    def add_usage(self, instance, collection_name):
        try:
            key = zope.traversing.api.getPath(instance)
        except TypeError:
            return
        if collection_name in self._usage.setdefault(key, ()):
            return
        self._usage[key] += (collection_name,)

        collection = getattr(instance.__class__, collection_name)
        if collection.back_reference:
            manager = gocept.reference.reference.get_manager()
            backref = collection.back_reference
            instances = self._find_backreferences()[backref]
            for target in self:
                other = manager.lookup_backreference(target, backref)
                if (len(instances) > 1
                    and not isinstance(other, ReferenceCollection)):
                    transaction.doom()
                    raise ValueError('Ambiguous back-reference.')
                other.reference(target, instance)

    def discard_usage(self, instance, collection_name):
        try:
            key = zope.traversing.api.getPath(instance)
        except TypeError:
            return
        if key not in self._usage:
            return
        names = self._usage.get(key)
        if collection_name not in names:
            return
        names = tuple(n for n in names if n != collection_name)
        if names:
            self._usage[key] = names
        else:
            del self._usage[key]

        # XXX remove back-references, possibly requires a backref counter

    def _register_all(self):
        for key in self._data:
            self._register_key(key)

    def _unregister_all(self):
        for key in self._data:
            self._unregister_key(key)

    def _register_key(self, key):
        try:
            gocept.reference.reference.lookup(key)
            gocept.reference.reference.get_manager().register_reference(key)
        except gocept.reference.interfaces.IntegrityError:
            # _register is called after data structures have been changed.
            transaction.doom()
            raise

    def _unregister_key(self, key):
        gocept.reference.reference.get_manager().unregister_reference(key)

    def __iter__(self):
        # The referencing collections have enough context to lookup a key, so
        # we just defer to them.
        for x in self._data:
            yield gocept.reference.reference.lookup(x)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return 'InstrumentedSet(%r)' % list(self._data)

    def reference(self, target):
        key = zope.traversing.api.getPath(target)
        # XXX provide test case for conditional increase
        if key not in self._data:
            self._data.insert(key)
            self._register_key(key)

    def unreference(self, target):
        key = zope.traversing.api.getPath(target)
        self._data.remove(key)
        self._unregister_key(key)

    def _find_backreferences(self):
        backrefs = {}
        for key, names in self._usage.items():
            instance = gocept.reference.reference.lookup(key)
            for name in names:
                collection = getattr(instance.__class__, name)
                if (isinstance(collection,
                               gocept.reference.reference.ReferenceBase)
                    and collection.back_reference):
                    backrefs.setdefault(
                        collection.back_reference, set()).add(instance)
        return backrefs

    def add(self, value):
        old_length = len(self._data)
        self.reference(value)
        if old_length == len(self._data):
            return

        manager = gocept.reference.reference.get_manager()
        for backref, instances in self._find_backreferences().iteritems():
            other = manager.lookup_backreference(value, backref)
            if (len(instances) > 1
                and not isinstance(other, ReferenceCollection)):
                transaction.doom()
                raise ValueError('Ambiguous back-reference.')
            for instance in instances:
                other.reference(value, instance)

    def remove(self, value):
        self.unreference(value)

        manager = gocept.reference.reference.get_manager()
        for backref, instances in self._find_backreferences().iteritems():
            other = manager.lookup_backreference(value, backref)
            for instance in instances:
                other.unreference(value, instance)

    def update(self, values):
        for value in values:
            self.add(value)

    def discard(self, value):
        key = zope.traversing.api.getPath(value)
        if key in self._data:
            self.remove(value)

    def pop(self):
        key = iter(self._data).next()
        self._data.remove(key)
        self._unregister_key(key)
        return gocept.reference.reference.lookup(key)

    def clear(self):
        self._unregister_all()
        self._data.clear()


def find_instrumented_sets(obj):
    for name in dir(obj):
        attr = getattr(obj, name, None)
        if isinstance(attr, InstrumentedSet):
            yield name, attr


@zope.component.adapter(zope.interface.Interface,
                        zope.container.interfaces.IObjectAddedEvent)
def ensure_usage_registration(obj, event):
    for name, value in find_instrumented_sets(obj):
        value.add_usage(obj, name)


@zope.component.adapter(zope.interface.Interface,
                        zope.container.interfaces.IObjectRemovedEvent)
def ensure_usage_unregistration(obj, event):
    for name, value in find_instrumented_sets(obj):
        value.discard_usage(obj, name)
