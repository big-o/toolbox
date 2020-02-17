#!/usr/bin/env python

import logging
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import numpy as np
import pandas as pd


__all__ = ["make_df", "to_sql"]
__author__ = "big-o"


def _prepare_fields(flds):
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


def _make_row(flds, rownum):
    row = {
        name: np.random.choice(fld["values"], p=fld["priors"])
        for name, fld in flds.items()
        if fld.get("repeat", True)
    }

    return row


def make_df(table, size, fields):
    """
    Create a random dataframe that follows the specified schema.
    """

    logger = logging.getLogger()
    fields = _prepare_fields(fields)
    data = []
    try:
        for i in tqdm(range(size), desc="Generating data"):
            data.append(_make_row(fields, i))
    except KeyboardInterrupt:
        # Catch Ctrl+C to just truncate the dataframe.
        logger.warning(f"Truncating data at {len(data)} rows.")

    df = pd.DataFrame(data)

    # Non-repeat fields weren't added. Add those now.
    for field, schema in fields.items():
        if not schema.get("repeat", True):
            vals = list(schema["values"])
            if size > len(vals):
                # Pad it out with a few NULLs
                vals = vals + [None] * (size - len(vals))
            col = np.random.choice(vals, replace=False, size=size)
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
    return df


def to_sql(df, url, db, if_exists):
    """
    Write the contents of a dataframe to a SQL database.
    """
    logger = logging.getLogger()
    engine = create_engine(url, pool_recycle=3600)
    conn = engine.connect()

    conn.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    conn.execute(f"USE {db}")
    if if_exists == "replace":
        # Bug workaround
        conn.execute(f"DROP TABLE IF EXISTS {df.name}")

    frame = df.to_sql(df.name, conn, index=False, if_exists=if_exists)

    conn.close()

    logger.info(
        f"Table `{db}:{df.name}' created successfully. Uploaded {len(df)} rows."
    )
