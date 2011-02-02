# vim:fileencoding=utf-8
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages


def read(filename):
    path = os.path.join('src', 'gocept', 'reference', filename)
    return file(path).read()


name = "gocept.reference"
version = '0.9.1'


setup(
    name = name,
    version = version,
    author = "gocept gmbh & co. kg",
    author_email = "developers@gocept.com",
    url = 'http://pypi.python.org/pypi/gocept.reference',
    description = "Intrinsic references for Zope/ZODB applications.",
    long_description = (
        open('README.txt').read() + "\n\n" +
        read('reference.txt') + "\n\n" +
        read('collection.txt') + "\n\n" +
        read('verify.txt') + "\n\n" +
        read('field.txt') + "\n\n" +
        open('CHANGES.txt').read()),
    license = "ZPL 2.1",
    keywords = "zodb zope3 intrinsic reference",
    classifiers = (
        "Topic :: Software Development",
        "Topic :: Database",
        "Framework :: ZODB",
        "Framework :: Zope3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: Zope Public License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ),
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = [
        'ZODB3',
        'setuptools',
        'transaction',
        'zope.annotation',
        'zope.component',
        'zope.container',
        'zope.deferredimport',
        'zope.generations',
        'zope.interface',
        'zope.schema >= 3.6.0',
        'zope.site',
        'zope.traversing',
        ],
    extras_require = {
        'test': ['zope.app.testing',
                 'zope.app.zcmlfiles',
                 ]
        },
    )
