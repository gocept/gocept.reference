=======
Changes
=======

0.11 (2020-09-10)
=================

- Add the possibility to commit savepoints and output progress for Fixer.


0.10 (2020-04-01)
=================

- Support Python 3.8.

- Use tox as only test setup.

- Switch dependency from ``ZODB3`` to ``ZODB``.

- Migrate to Github.


0.9.4 (2017-05-15)
==================

- Version 0.9.3 did not include all files. Fixing this by adding a
  MANIFEST.in.


0.9.3 (2017-05-14)
==================

- Use `pytest` as test runner.


0.9.2 (2015-08-05)
==================

- Move repos to https://bitbucket.org/gocept/gocept.reference


0.9.1 (2011-02-02)
==================

- Bug fixed: reference descriptors could not find out their attribute names
  when read from the class.

- Bug fixed: the algorithm for digging up the attribute name of a reference
  descriptor on a class would not handle inherited references.


0.9.0 (2010-09-18)
==================

- Depending on ``zope.generations`` instead of ``zope.app.generations``.


0.8.0 (2010-08-20)
==================

- Updated tests to work with `zope.schema` 3.6.

- Removed unused parameter of ``InstrumentedSet.__init__``.

- Avoid ``sets`` module as it got deprecated in Python 2.6.


0.7.2 (2009-06-30)
==================

- Fixed generation added in previous version.


0.7.1 (2009-04-28)
==================

- Fixed reference counting for reference collections by keeping a usage
  counter for InstrumentedSets.

- Added a tool that rebuilds all reference counts. Added a database generation
  that uses this tool to set up the new usage counts for InstrumentedSets.


0.7.0 (2009-04-06)
==================

- Require newer ``zope.app.generations`` version to get rid of
  dependency on ``zope.app.zopeappgenerations``.


0.6.2 (2009-03-27)
==================

- Validation of ``gocept.reference.field.Set`` now allows both
  ``InstrumentedSet`` and ``set`` in field validation, as both
  variants occur.


0.6.1 (2009-03-27)
==================

- ``zope.app.form`` breaks encapsulation of the fields by using the
  ``_type`` attribute to convert form values to field values. Using
  ``InstrumentedSet`` as ``_type`` was a bad idea, as only the
  reference collection knows how to instantiate an
  ``InstrumentedSet``. Now the trick is done on validation where the
  ``_type`` gets set to ``InstrumentedSet`` temporarily.


0.6 (2009-03-26)
================

- Take advantage of the simpler zope package dependencies achieved at the Grok
  cave sprint in January 2009.

- Added zope.schema field ``gocept.reference.field.Set`` which has the
  internally used InstrumentedSet as field type, so validation does
  not fail.

- gocept.reference 0.5.2 had a consistency bug: Causing a TypeError by
  trying to assign a non-collection to a ReferenceCollection attribute
  would break integrity enforcement for that attribute while keeping
  its previously assigned value.


0.5.2 (2008-10-16)
==================

- Fixed: When upgrading gocept.reference to version 0.5.1, a
  duplication error was raised.


0.5.1 (2008-10-10)
==================

- Made sure that the reference manager is installed using
  zope.app.generations before other packages depending on
  gocept.reference.

0.5 (2008-09-11)
================

- Added specialized variant of zope.interface.verify.verifyObject
  which can handle references and reference collections correctly.


0.4 (2008-09-08)
================

- Moved InstrumentedSet to use BTree data structures for better performance.

- Added `update` method to InstrumentedSet.

- Updated documentation.


0.3 (2008-04-22)
================

- Added a `set` implementation for referencing collections of objects.

0.2 (2007-12-21)
================

- Extended the API for `IReferenceTarget.is_referenced` to allow specifying
  whether to query for references recursively or only on a specific object.
  By default the query is recursive.

- Fixed bug in the event handler for enforcing ensured constraints: referenced
  objects could be deleted if they were deleted together with a parent
  location.

0.1 (2007-12-20)
================

Initial release.
