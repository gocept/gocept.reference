# Make this a Python package

import zope.deferredimport

zope.deferredimport.define(
    Reference='gocept.reference.reference:Reference',
    ReferenceCollection='gocept.reference.collection:ReferenceCollection')
