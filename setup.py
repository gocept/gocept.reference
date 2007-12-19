# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages

name = "gocept.reference"
setup(
    name = name,
    version = "1.0dev",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
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
                        'zope.annotation',
                        'zope.traversing'],
    extras_require = {
        'test': ['zope.app.container']
    },
    entry_points = {
        'zc.buildout': [
            'default = %s.recipe:Recipe [recipe]' % name,
        ]},
    )
