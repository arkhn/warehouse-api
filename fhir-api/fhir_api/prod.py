from uwsgidecorators import postfork

from app import create_app
from db import get_store, reset_db_connection


@postfork
def on_fork_do():
    reset_db_connection()
    get_store()


app = create_app()
