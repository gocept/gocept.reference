============
Introduction
============

This package provides a reference implementation.

The specific properties of this implementation are:

- intended to be used for intrinsic references

- provides integrity enforcement

- modelled partially after relational `foreign keys`

.. contents::


Motivation
==========

When developing an application we often find the need to reference objects
that are stored as application data. Examples of such objects include
centrally managed 'master data'.

The reference to those objects is typically intrinsic to the application we
develop so they should behave like normal Python object references while being
under the control of our application.

Within the world of Zope and ZODB there are different ways to achieve this. The
various approaches have different semantics and side effects. Our goal is to
unify the way of intrinsically referencing objects and to provide the ability to
switch between different semantics as needed without rewriting application code
and without the need to migrate persistent data structures (at least from the
application's point of view).


Model comparison
================

Our goal was to determine the advantages and disadvantages of the different
existing approaches. We included three general approaches from the world of
Python/Zope/ZODB as well as the standard relational approach to normalisation
tables.

We used four criteria to describe each solution:

Reference data
  What data is stored to describe the reference?

Reference semantics
  What meaning does the reference have? How can its meaning change?

Integrity
  What might happen to the application if data that is involved in the
  reference changes or is deleted?

Set/Lookup
  What does the application developer have to do to set a reference or
  look up a referenced object?


======================    =========================================     ===========================================   ========================================    ====================================================
Property                  Python references                              Weak references                              Key reference                               Relational DBs
======================    =========================================     ===========================================   ========================================    ====================================================
Reference data            OID                                           OID                                           application-specific key                    application-specific (primary key + table name)

Reference semantics       Refers to a specific                          Refers to a specific                          Refers to an object which                   Refers to an object (row) that is associated
                          Python object                                 Python object                                 is associated with the saved key            with the primary key at the time of the lookup.
                                                                                                                      at the time of the lookup.

Integrity                 The reference stays valid, however,           The reference might have become stale         The reference might have become             Dependening on the use of `foreign keys`
                          the target object might have lost its         and leave the referencing object in an        stale.                                      and the databases implementation of constraints.
                          meaning for the application.                  invalid state.                                                                            Can usually be forced to stay valid.

Set/Lookup                Normal Python attribute access.               Use WeakRef wrapper to store and              Depends on the implementation.              Explicitly store the primary key.
                                                                        __call__ to lookup. Might use properties      Might use properties for convenience.       Use JOIN to look up.
                                                                        for convenience.
======================    =========================================     ===========================================   ========================================    ====================================================


Observations
============

- Relational: every object (row) has a canonical place that defines a primary
  key.

  The ZODB (like a filesystem) can have multiple hard links to an object.
  Objects are deleted when the last hard link to an object is removed. This
  makes it impossible to use hard links for referencing an object because
  object deletion will not be noticed and the objects will continue to live.
  The ZODB itself does not have a notion of a canonical place where an object
  is defined.

- Relational: When referencing an object we can enforce integrity by declaring
  a foreign key. This is orthogonal to the data stored.

- Relational: As an application-level key is used for identifying the target
  of a reference, the application can choose to delete a row and re-add a row
  with the same primary key later. If the integrity is enforced this requires
  support on the database level to temporarily ignore broken foreign keys.

- Normal Python references embed themselves naturally in the application.
  Properties allow hiding the implementation of looking up and storing
  references.


Conclusions & Requirements for the reference implementation
===========================================================

- Allow configuration of `foreign key` constraints (none, always, at the end
  of the transaction). This configuration must be changable at any time with
  an automatic migration path provided.

- Use application level keys to refer to an object.

- Use a canonical location and a primary key to store objects and to determine
  whether an object was deleted.

- Distinguish between two use cases when modifying an object's key:

  1. The application references the right object but has the wrong key (as the
     key itself might have meaning for the application). In this case the
     object must be updated to receive the new, correct key and the references
     must be updated to refer to this new key.

  2. The application references the wrong object with the right key. In this
     case the object referenced by the key must be replaced with a different
     object.


Implementation notes
====================

- Canonical location is determined by location/containment. The primary key for
  a reference is the referenced object's location.

- Constraints are enforced by monitoring containment events.

- The different ways of updating/changing a key's meaning are supported by an
  indirection that enumerates all keys and stores a `reference id` on the
  referencing object instead of the location. The two use cases for changing
  the meaning are implemented by:

  1. associating a new path with an existing reference id

  2. associating a new reference id with an existing path
