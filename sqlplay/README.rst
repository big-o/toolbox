SQLPlay
=======

Generates tables of random SQL data based on the schemas you define.

A "schema" consists of the table size, table field names and possible values. You can
specify whether to randomly select values from the allowed choices with replacement
(default) or without. ``tables.py`` gives you an example of a valid schema config file
that creates a few tables.

Usage
-----

.. code-block:: bash

   python -m sqlplay -u "mysql://user@localhost" -c path/to/tables.py
