#!/usr/bin/env python

import click
from sqlalchemy import create_engine
import numpy as np
import pandas as pd


__all__ = ["main"]
__author__ = "big-o"


# TODO: Make field names and values configurable.
_DATERNG = pd.Timedelta(weeks=8)
_FLDS = {"userid": range(100), "action": ["on", "off"]}


def prepare_fields(flds):
    flds = flds.copy()
    flds["_timestamp"] = pd.date_range(
        pd.Timestamp.now() - _DATERNG,
        periods=_DATERNG.total_seconds() // 60,
        freq="min",
    )

    for key in flds:
        vals = flds[key]
        # Create random priors for each value.
        p = np.random.normal(size=len(vals))
        # Softmax to get probabilities.
        priors = np.exp(p) / np.exp(p).sum()

        flds[key] = vals, priors

    return flds


def make_row(flds):
    row = {
        fld: np.random.choice(vals, p=priors) for fld, (vals, priors) in flds.items()
    }

    return row


@click.command()
@click.option(
    "-u",
    "--url",
    required=True,
    help="SQL URL to make connection with, e.g. 'mysql://user@localhost'.",
)
@click.option(
    "-c",
    "--row-count",
    default=10000,
    type=click.IntRange(0, 10000, clamp=True),
    help="Number of rows to create in table",
)
@click.option("-d", "--db", default="play", help="Database name")
@click.option("-t", "--table", default="play", help="Table name")
@click.option(
    "-e",
    "--if-exists",
    default="fail",
    type=click.Choice(["append", "fail", "replace"]),
    help="Table name",
)
@click.option(
    "-C",
    "--config",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help=(
        "Optional config file. Should contain dicts of field names -> "
        "sequence of possible values called `fields'. "
        "The dict names will be used as table names."
    ),
)
def main(url, row_count, db, table, if_exists, config):
    if config is None:
        flds = _FLDS
        flds = prepare_fields(flds)
        make_table(url, row_count, db, if_exists, table, flds)
    else:
        from importlib.util import spec_from_file_location, module_from_spec

        spec = spec_from_file_location("config", config)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        tbls = [getattr(mod, tbl) for tbl in dir(mod) if not tbl.startswith("_")]
        for tbl in tbls:
            tbl = tbl.copy()
            tbl["fields"] = prepare_fields(tbl["fields"])
            make_table(url, row_count, db, if_exists, **tbl)


def make_table(url, row_count, db, if_exists, table, fields):

    df = pd.DataFrame([make_row(fields) for i in range(row_count)])
    df.sort_values("_timestamp", inplace=True)
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
