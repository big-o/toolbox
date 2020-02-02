#!/usr/bin/env python

import click
from sqlalchemy import create_engine
import numpy as np
import pandas as pd


__all__ = ["main"]
__author__ = "big-o"


# TODO: Make field names and values configurable.
_DATERNG = pd.Timedelta(weeks=8)
_FLDS = {
    "userid": range(100),
    "action": ["on", "off"],
    "timestamp": pd.date_range(
        pd.Timestamp.now() - _DATERNG,
        periods=_DATERNG.total_seconds() // 60,
        freq="min",
    ),
}

for key in _FLDS:
    vals = _FLDS[key]
    # Create random priors for each value.
    p = np.random.normal(size=len(vals))
    # Softmax to get probabilities.
    priors = np.exp(p) / np.exp(p).sum()
    _FLDS[key] = vals, priors


def make_row():
    row = {
        fld: np.random.choice(vals, p=priors) for fld, (vals, priors) in _FLDS.items()
    }

    return row


@click.command()
@click.option("-u", "--url", required=True, help="SQL URL to make connection with, e.g. 'mysql://user@localhost'.")
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
def main(url, row_count, db, table, if_exists):
    df = pd.DataFrame([make_row() for i in range(row_count)])
    df.sort_values("timestamp", inplace=True)
    df.name = table

    engine = create_engine(url, pool_recycle=3600)
    conn = engine.connect()

    conn.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    conn.execute(f"USE {db}")
    frame = df.to_sql(df.name, conn, index=False, if_exists=if_exists)

    conn.close()

    print(f"Table `{db}:{table}' created successfully.")


if __name__ == "__main__":
    main()
