import gocept.reference.testing


def test_suite():
    return gocept.reference.testing.FunctionalDocFileSuite(
        'reference.txt',
        'collection.txt',
        'verify.txt',
        'regression.txt',
        'field.txt',
        'fix.txt',
    )
