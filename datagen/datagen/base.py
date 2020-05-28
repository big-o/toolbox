#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from rich.console import Console
from rich.progress import track
import numpy as np
import pandas as pd
from scipy.linalg import eigh


__all__ = ["make_df", "to_sql"]
__author__ = "big-o"


console = Console()


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


def _validate_corr(corr):
    if not isinstance(corr, pd.DataFrame):
        raise ValueError("correlation matrix must be a pandas DataFrame.")

    nflds = len(flds)
    if corr.shape != (nflds, nflds):
        raise ValueError(
            "correlation matrix must be square and have one column/row for each field "
            "in your schema."
        )

    if not all(np.issubdtype(t, np.number) for t in corr.dtypes):
        raise ValueError("correlation matrix must be numeric.")

    try:
        corr = corr[flds].loc[flds]
    except KeyError:
        raise ValueError(
            "correlation matrix index and columns must be the field names for your "
            "schema."
        )

    if not np.allclose(corr, corr.T):
        raise ValueError("correlation matrix must be symmetric")

    return corr


def make_df(table, size, fields, corr=None):
    """
    Create a random dataframe that follows the specified schema.
    """

    fields = _prepare_fields(fields)
    data = []

    # Generate
    try:
        for i in track(range(size), description="Generating data..."):
            data.append(_make_row(fields, i))
    except KeyboardInterrupt:
        # Catch Ctrl+C to just truncate the dataframe.
        console.log(f"[white on red]Truncating data at [bold]{len(data)}[/] rows.[/]")

    df = pd.DataFrame(data)

    # Non-repeat fields weren't added. Add those now.
    for field, schema in fields.items():
        if not schema.get("repeat", True):
            vals = list(schema["values"])
            if size > len(vals):
                # Pad it out with a few NULLs
                vals = vals + [None] * (size - len(vals))

            # Use len(df) instead of size in case it was truncated.
            col = np.random.choice(vals, replace=False, size=len(df))
            df[field] = col

    # Reset the ordering
    flds = list(fields.keys())
    df = df[flds]

    # Alter the random values to add in any correlation if requested.
    if corr is not None:
        # corr must be a square dataframe with the indices and columns being the
        # fields.
        corr = _validate_corr(corr)

        # Compute the eigenvalues and eigenvectors.
        evals, evecs = eigh(corr)
        # Construct c, so c*c^T = corr.
        c = np.dot(evecs, np.diag(np.sqrt(evals)))

        # Convert the data to correlated random variables.
        df[:] = np.dot(c, df.values)

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
    engine = create_engine(url, pool_recycle=3600)
    conn = engine.connect()

    # conn.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    # conn.execute(f"USE {db}")
    if not database_exists(url):
        create_database(url)

    if if_exists == "replace":
        # Bug workaround
        conn.execute(f"DROP TABLE IF EXISTS {df.name}")

    frame = df.to_sql(df.name, conn, index=False, if_exists=if_exists)

    conn.close()

    console.log(
        f"Table [bold magenta]`{db}:{df.name}'[/] created successfully. "
        f"Uploaded [italic red]{len(df)}[/] rows."
    )
