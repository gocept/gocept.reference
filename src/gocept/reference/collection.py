# vim:fileencoding=utf-8
# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Reference lists."""

import BTrees.OOBTree
import persistent
import transaction
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
        if isinstance(value, (set, frozenset)):
            value = InstrumentedSet(value)
        if value is not None and not isinstance(value, InstrumentedSet):
            raise TypeError("%r can't be assigned as a reference collection: "
                            "only sets are allowed." % value)
        self._unregister(instance)
        storage = gocept.reference.reference.get_storage(instance)
        storage[self.__name__] = value
        if value is not None:
            self._register(instance)

    def _unregister(self, instance):
        if not self.needs_registration(instance):
            return
        target_set = gocept.reference.reference.get_storage(
            instance).get(self.__name__)
        if target_set is not None:
            target_set.unregister_usage()

    def _register(self, instance):
        if not self.needs_registration(instance):
            return
        target_set = gocept.reference.reference.get_storage(
            instance).get(self.__name__)
        if target_set is not None:
            target_set.register_usage()


class InstrumentedSet(persistent.Persistent):

    _ensured_usage_count = 0

    def __init__(self, src):
        # Convert objects to their keys
        self._data = BTrees.OOBTree.TreeSet(
            zope.traversing.api.getPath(item) for item in src)

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

    def add(self, value):
        key = zope.traversing.api.getPath(value)
        if key not in self._data:
            self._data.insert(key)
            self._register_key(key)

    def remove(self, value):
        key = zope.traversing.api.getPath(value)
        self._data.remove(key)
        self._unregister_key(key)

    def update(self, values):
        for value in values:
            self.add(value)

    def discard(self, value):
        key = zope.traversing.api.getPath(value)
        if key in self._data:
            self._unregister_key(key)
            self._data.remove(key)

    def pop(self):
        key = next(iter(self._data))
        self._data.remove(key)
        self._unregister_key(key)
        return gocept.reference.reference.lookup(key)

    def clear(self):
        for key in self._data:
            self._unregister_key(key)
        self._data.clear()
