# vim:fileencoding=utf-8
import os.path
from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join('src', 'gocept', 'reference', filename)) as f:
        return f.read()


name = "gocept.reference"
version = '0.11'


setup(
    name=name,
    version=version,
    author="gocept gmbh & co. kg",
    author_email="mail@gocept.com",
    url='https://github.com/gocept/gocept.reference',
    description="Intrinsic references for Zope/ZODB applications.",
    long_description=(
        open('COPYRIGHT.txt').read() + "\n\n" +
        open('README.rst').read() + "\n\n" +
        read('reference.txt') + "\n\n" +
        read('collection.txt') + "\n\n" +
        read('verify.txt') + "\n\n" +
        read('field.txt') + "\n\n" +
        open('CHANGES.rst').read()),
    license="ZPL 2.1",
    keywords="zodb zope3 intrinsic reference",
    classifiers=(
        "Topic :: Software Development",
        "Topic :: Database",
        "Framework :: ZODB",
        "Framework :: Zope3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Zope Public License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ),
    zip_safe=False,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['gocept'],
    install_requires=[
        'BTrees',
        'ZODB',
        'persistent',
        'setuptools',
        'six',
        'transaction',
        'zope.annotation',
        'zope.component',
        'zope.container',
        'zope.deferredimport',
        'zope.generations',
        'zope.interface',
        'zope.location',
        'zope.schema >= 3.6.0',
        'zope.traversing',
    ],
    extras_require={
        'test': ['zope.app.testing',
                 'zope.app.zcmlfiles',
                 'gocept.pytestlayer',
                 'mock ; python_version=="2.7"',  # PY2
                 ]
    },
)
