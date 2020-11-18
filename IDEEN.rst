==========================
Ideen für gocept.reference
==========================

Registrierung
=============

Probleme
--------

- Integritätssicherung benutzt eine bedingte Registrierung von Referenzen:
  komplexe Logik, wann was zu registrieren und zu deregistrieren ist,
  inkonsistent, nachdem das Sicherungs-Flag im Code geändert wurde

- Das erzeugt direkt einen Bug für Referenzmengen ohne Integritätssicherung:
  bei der Zuweisung einer Menge mit Elementen werden die Elemente nicht
  registriert, aber beim Entfernen aus der Menge bedingungslos genau einmal
  deregistriert. Die tatsächliche Anzahl zu deregistrierender Referenzen kann
  nicht bestimmt werden, solange die Verwendungen eines InstrumentedSet
  (zumindest die mit Integritätssicherung) nicht gespeichert werden.

- mehrfache Verwendung von Referenzmengen sowohl für Registrierung als auch
  für Rückreferenzen unüberschaubar

- keine Introspektion der Referenzen möglich

Lösungsansatz
-------------

- immer alle Referenzen (nicht nur die Anzahl gesicherter Referenzen)
  registrieren

- Mehrfachverwendungen einer Menge im Manager speichern

- Alternativ: Referenzierende Objekte als Annotationen an Referenzzielen
  speichern, evtl. auf Manager völlig verzichten.

Mengen instrumentieren
======================

- Proxys statt InstrumentedSet benutzen

Kopplung
========

- evtl. Ereignisse beim Referenzieren und Dereferenzieren auslösen, um
  Integritätssicherung, Rückreferenzen usw. anzubinden
