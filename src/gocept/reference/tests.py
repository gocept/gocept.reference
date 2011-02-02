# -*- coding: latin-1 -*-
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Tests for gocept.reference"""

import unittest
import zope.interface.verify

import gocept.reference.content
import gocept.reference.interfaces
import gocept.reference.manager
import gocept.reference.testing


class TestInterfaces(unittest.TestCase):

    def test_IReferenceSource(self):
        zope.interface.verify.verifyObject(
            gocept.reference.interfaces.IReferenceSource,
            gocept.reference.content.ReferenceSource(object))

    def test_IReferenceTarget(self):
        zope.interface.verify.verifyObject(
            gocept.reference.interfaces.IReferenceTarget,
            gocept.reference.content.ReferenceTarget(object))

    def test_IReferenceManager(self):
        zope.interface.verify.verifyObject(
            gocept.reference.interfaces.IReferenceManager,
            gocept.reference.manager.ReferenceManager())


class TestContentFunctions(unittest.TestCase):

    def test_find_references_handles_broken_attributes(self):
        class BrokenDescriptor(object):
            def __get__(self, instance, *args, **kw):
                raise AttributeError()
        class BrokenAttribute(object):
            asdf = BrokenDescriptor()
        obj = BrokenAttribute()
        self.assertEquals(
            [],
            list(gocept.reference.content.find_references(obj)))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInterfaces))
    suite.addTest(unittest.makeSuite(TestContentFunctions))
    suite.addTest(gocept.reference.testing.FunctionalDocFileSuite(
            'reference.txt',
            'collection.txt',
            'verify.txt',
            'regression.txt',
            'field.txt',
            'fix.txt',
            ))
    return suite
