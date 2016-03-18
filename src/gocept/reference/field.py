# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.schema
import gocept.reference.collection
import zope.schema._bootstrapinterfaces


class Set(zope.schema.Set):
    """A set field using the InstrumentedSet class."""

    _internal_type = gocept.reference.collection.InstrumentedSet

    def _validate(self, value):
        # We need to clone the field here to make sure that setting
        # the _type for validation does not have impact on other
        # instances
        if isinstance(value, self._type):
            validation_type = self._type
        elif isinstance(value, self._internal_type):
            validation_type = self._internal_type
        else:
            raise zope.schema._bootstrapinterfaces.WrongType(
                value, (self._type, self._internal_type))
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone._type = validation_type
        super(Set, clone)._validate(value)
