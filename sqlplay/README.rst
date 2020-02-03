SQLPlay
=======

Generates tables of random data based on the schemas you define, and loads them into a
SQL database of your choice.

A "schema" consists of the table size, table field names and possible values. You can
specify whether to randomly select values from the allowed choices with replacement
(default) or without. ``tables.py`` gives you an example of a valid schema config file
that creates a few tables.

Usage
-----

.. code-block:: bash

   python -m sqlplay -u "mysql://user@localhost" -c path/to/tables.py

Any flavour of SQL supported by :mod:`sqlalchemy` may be used.
