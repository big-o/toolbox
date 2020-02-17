from importlib.util import spec_from_file_location, module_from_spec
import click
import logging

from .base import *

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
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s:%(funcName)s: %(message)s"
    )
    logger = logging.getLogger()

    spec = spec_from_file_location("config", config)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    tbls = mod.schema

    for name, schema in tbls.items():
        schema = schema.copy()
        df = make_df(table=name, **schema)
        if click.confirm(f"{len(df)} records generated. Upload to {db} database?"):
            to_sql(df, url, db, if_exists)
        else:
            logger.warning("Operation aborted at user's request.")


if __name__ == "__main__":
    main()
