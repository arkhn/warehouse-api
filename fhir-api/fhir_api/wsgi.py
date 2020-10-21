from uwsgidecorators import postfork

from fhir_api.app import app  # noqa
from fhir_api.db import get_store, reset_db_connection


@postfork
def on_fork_do():
    reset_db_connection()
    get_store()
