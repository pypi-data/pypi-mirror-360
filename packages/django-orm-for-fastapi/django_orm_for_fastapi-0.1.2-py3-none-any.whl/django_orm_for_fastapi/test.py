from typing import List

from django.test.utils import setup_databases, teardown_databases
from django.core.management import call_command

from .consts import DEFAULT_CONNECTION_ID
from .functions import create_db_tables

def create_test_database(create_tables: bool = True, verbosity: int = 0):
    setup_databases_args = {}

    setup_databases_args["keepdb"] = True

    db_cfg = setup_databases(
        verbosity=verbosity,
        interactive=False,
        aliases=[DEFAULT_CONNECTION_ID],
        # serialized_aliases=serialized_aliases,
        **setup_databases_args,
    )

    if create_tables:
        create_db_tables()

    return db_cfg

def destroy_test_database(
    db_config: List,
    keepdb: bool = False,
    verbosity: int = 0,
):
    teardown_databases(db_config, verbosity=verbosity, keepdb=keepdb)


def flush_test_database(
):
    call_command(
        "flush",
        verbosity=0,
        interactive=False,
        database=DEFAULT_CONNECTION_ID,
        reset_sequences=False,
        allow_cascade=True,
    )

