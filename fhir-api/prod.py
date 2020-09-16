from uwsgidecorators import postfork

from db import get_store, reset_db_connection
from main import create_app


@postfork
def on_fork_do():
    reset_db_connection()
    get_store()


app = create_app()
