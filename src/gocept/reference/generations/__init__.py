# vim:fileencoding=utf-8
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Database initialisation and upgrading."""

from zope.generations.generations import SchemaManager


manager = SchemaManager(
    minimum_generation=1,
    generation=2,
    package_name='gocept.reference.generations')
