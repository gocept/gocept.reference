# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages


name = "gocept.reference"
setup(
    name = name,
    version = "0.3",
    author = "gocept gmbh & co. kg",
    author_email = "developers@gocept.com",
    description = "Intrinsic references for Zope/ZODB applications.",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zodb zope3",
    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = ['setuptools',
                        'ZODB3',
                        'zope.interface',
                        'zope.component',
                        'zope.annotation',
                        'zope.traversing',
                        'zope.deferredimport',
                        'zope.app.container',
                        ],
    extras_require = {
        'test': ['zope.app.testing']
    },
    )
