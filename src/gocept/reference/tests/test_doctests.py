import gocept.reference.content
import gocept.reference.interfaces
import gocept.reference.manager
import gocept.reference.testing
import unittest
import zope.interface.verify


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
        class BrokenDescriptor:
            def __get__(self, instance, *args, **kw):
                raise AttributeError()

        class BrokenAttribute:
            asdf = BrokenDescriptor()
        obj = BrokenAttribute()
        self.assertEqual(
            [],
            list(gocept.reference.content.find_references(obj)))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
        TestInterfaces))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
        TestContentFunctions))
    suite.addTest(gocept.reference.testing.FunctionalDocFileSuite(
        'reference.txt',
        'collection.txt',
        'verify.txt',
        'regression.txt',
        'field.txt',
        'fix.txt',
    ))
    return suite
