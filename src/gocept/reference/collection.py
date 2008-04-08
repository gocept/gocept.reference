# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Reference lists."""

import sets

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
            target_set = self.storage(instance)[self.__name__]
        except KeyError:
            raise AttributeError(self.__name__)
        return target_set

    @gocept.reference.reference.find_name
    def __set__(self, instance, value):
        self._unregister(instance)
        storage = self.storage(instance)
        if value is None:
            storage[self.__name__] = None
            return
        if isinstance(value, (set, sets.BaseSet)):
            value = InstrumentedSet(value, self)
        elif isinstance(value, InstrumentedSet):
            value._register_collection(self)
        else:
            raise TypeError("%r can't be assigned as a reference collection: "
                            "only sets are allowed." % value)
        storage[self.__name__] = value
        self._register(instance)

    def _unregister(self, instance):
        if not self.needs_registration(instance):
            return
        target_set = self.storage(instance).get(self.__name__)
        if not target_set:
            return
        target_set._unregister_all()

    def _register(self, instance):
        if not self.needs_registration(instance):
            return
        target_set = self.storage(instance).get(self.__name__)
        if target_set is None:
            return
        target_set._register_all()


class InstrumentedSet(persistent.Persistent):

    def __init__(self, src, collection):
        # Convert objects to their keys
        self._data = set(zope.traversing.api.getPath(item) for item in src)
        self._referencing_collections = persistent.list.PersistentList()
        self._register_collection(collection)

    def _register_collection(self, collection):
        if collection not in self._referencing_collections:
            self._referencing_collections.append(collection)

    def _unregister_collection(self, collection):
        self._referencing_collections.remove(collection)

    def _register_all(self):
        for key in self._data:
            self._register_key(key)

    def _unregister_all(self):
        for key in self._data:
            self._unregister_key(key)

    def _register_key(self, key):
        try:
            self.lookup(key)
            self.manager.register_reference(key)
        except gocept.reference.interfaces.IntegrityError:
            # _register is called after data structures have been changed.
            transaction.doom()
            raise

    def _unregister_key(self, key):
        self.manager.unregister_reference(key)

    @property
    def manager(self):
        return self._referencing_collections[0].manager

    @property
    def lookup(self):
        return self._referencing_collections[0].lookup

    def __iter__(self):
        # The referencing collections have enough context to lookup a key, so
        # we just defer to them.
        for x in self._data:
            yield self.lookup(x)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return 'InstrumentedSet(%r)' % list(self._data)

    def add(self, value):
        key = zope.traversing.api.getPath(value)
        self._data.add(key)
        self._p_changed = True
        self._register_key(key)

    def remove(self, value):
        key = zope.traversing.api.getPath(value)
        self._data.remove(key)
        self._p_changed = True
        self._unregister_key(key)

    def discard(self, value):
        key = zope.traversing.api.getPath(value)
        if key in self._data:
            self._unregister_key(key)
        self._data.discard(key)
        self._p_changed = True

    def pop(self):
        key = self._data.pop()
        self._unregister_key(key)
        self._p_changed = True
        return self.lookup(key)

    def clear(self):
        self._unregister_all()
        self._data.clear()
        self._p_changed = True
