# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.schema
import gocept.reference.collection

class Set(zope.schema.Set):
    """A set field using the InstrumentedSet class."""

    _type = gocept.reference.collection.InstrumentedSet
