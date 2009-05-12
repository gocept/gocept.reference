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

    def reference(self, instance, targets):
        getattr(instance, self.__name__).reference(targets)

    def unreference(self, instance, targets):
        getattr(instance, self.__name__).unreference(targets)

    def _unregister(self, instance):
        target_set = gocept.reference.reference.get_storage(
            instance).get(self.__name__)
        if target_set is None:
            return
        target_set.discard_usage(instance, self.__name__)
        if self.needs_registration(instance):
            target_set.unregister_usage()

    def _register(self, instance):
        target_set = gocept.reference.reference.get_storage(
            instance).get(self.__name__)
        if target_set is None:
            return
        target_set.add_usage(instance, self.__name__)
        if self.needs_registration(instance):
            target_set.register_usage()


class InstrumentedSet(persistent.Persistent):

    _ensured_usage_count = 0

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
                other.reference(target, [instance])

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

        collection = getattr(instance.__class__, collection_name)
        if collection.back_reference:
            manager = gocept.reference.reference.get_manager()
            for target in self:
                other = manager.lookup_backreference(
                    target, collection.back_reference)
                other.unreference(target, [instance])

    def register_usage(self):
        self._ensured_usage_count += 1
        for key in self._data:
            self._register_key(key, count=1)

    def unregister_usage(self):
        self._ensured_usage_count -= 1
        for key in self._data:
            self._unregister_key(key, count=1)

    def _register_key(self, key, count=None):
        gocept.reference.reference.lookup(key)
        if count is None:
            count = self._ensured_usage_count
        try:
            gocept.reference.reference.get_manager().register_reference(
                key, count)
        except gocept.reference.interfaces.IntegrityError:
            # _register is called after data structures have been changed.
            transaction.doom()
            raise

    def _unregister_key(self, key, count=None):
        if count is None:
            count = self._ensured_usage_count
        gocept.reference.reference.get_manager().unregister_reference(
            key, count)

    def __iter__(self):
        # The referencing collections have enough context to lookup a key, so
        # we just defer to them.
        for x in self._data:
            yield gocept.reference.reference.lookup(x)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return 'InstrumentedSet(%r)' % list(self._data)

    def reference(self, targets):
        for target in targets:
            key = zope.traversing.api.getPath(target)
            if key not in self._data:
                self._data.insert(key)
                self._register_key(key)

    def unreference(self, targets):
        for target in targets:
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
                        collection.back_reference, []).append(instance)
        return backrefs

    def add(self, value):
        old_length = len(self._data)
        self.reference([value])
        if old_length == len(self._data):
            return

        manager = gocept.reference.reference.get_manager()
        for backref, instances in self._find_backreferences().iteritems():
            other = manager.lookup_backreference(value, backref)
            other.reference(value, instances)

    def remove(self, value):
        self.unreference([value])

        manager = gocept.reference.reference.get_manager()
        for backref, instances in self._find_backreferences().iteritems():
            other = manager.lookup_backreference(value, backref)
            other.unreference(value, instances)

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
        for key in list(self._data):
            value = gocept.reference.reference.lookup(key)
            self.remove(value)
