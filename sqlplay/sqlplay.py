#!/usr/bin/env python

import click
from importlib.util import spec_from_file_location, module_from_spec
from sqlalchemy import create_engine
import numpy as np
import pandas as pd


__all__ = ["main"]
__author__ = "big-o"


def prepare_fields(flds):
    flds = flds.copy()

    for key in flds:
        fld = flds[key]
        if "priors" not in fld and fld.get("repeat", True):
            vals = fld["values"]
            # Create random priors for each value.
            p = np.random.normal(size=len(vals))
            # Softmax to get probabilities.
            priors = np.exp(p) / np.exp(p).sum()

            fld["priors"] = priors

    return flds


def make_row(flds):
    row = {
        name: np.random.choice(fld["values"], p=fld["priors"])
        for name, fld in flds.items()
        if fld.get("repeat", True)
    }

    return row


@click.command()
@click.option(
    "-u",
    "--url",
    required=True,
    help="SQL URL to make connection with, e.g. 'mysql://user@localhost'.",
)
@click.option("-d", "--db", default="play", help="Database name")
@click.option(
    "-e",
    "--if-exists",
    default="fail",
    type=click.Choice(["append", "fail", "replace"]),
    help="Table name",
)
@click.option(
    "-c",
    "--config",
    required=True,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help=(
        "Optional config file. Should contain dicts of field names -> "
        "sequence of possible values called `fields'. "
        "The dict names will be used as table names."
    ),
)
def main(url, db, if_exists, config):
    spec = spec_from_file_location("config", config)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    tbls = mod.schema

    for name, schema in tbls.items():
        schema = schema.copy()
        schema["fields"] = prepare_fields(schema["fields"])
        make_table(url, db, if_exists, table=name, **schema)


def make_table(url, db, if_exists, table, size, fields):
    df = pd.DataFrame([make_row(fields) for i in range(size)])
    # Non-repeat fields weren't added. Add those now.
    for field, schema in fields.items():
        if not schema.get("repeat", True):
            vals = schema["values"]
            if size > len(vals):
                vals = vals + [None] * (size - len(vals))
            col = np.random.choice(vals, replace=False, size=len(vals))
            if size < len(vals):
                col = col[:size]

            df[field] = col

    # Reset the ordering
    df = df[list(fields.keys())]

    sort_cols = [
        (fields[fld]["sort"], fld) for fld in fields if fields[fld].get("sort", False)
    ]
    if len(sort_cols) > 0:
        sort_cols.sort()
        sort_cols = [f[1] for f in sort_cols]
        df.sort_values(sort_cols, inplace=True)

    df.name = table

    engine = create_engine(url, pool_recycle=3600)
    conn = engine.connect()

    conn.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    conn.execute(f"USE {db}")
    if if_exists == "replace":
        # Bug workaround
        conn.execute(f"DROP TABLE IF EXISTS {table}")

    frame = df.to_sql(table, conn, index=False, if_exists=if_exists)

    conn.close()

    print(f"Table `{db}:{table}' created successfully.")


if __name__ == "__main__":
    main()
