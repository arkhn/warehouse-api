import fhirbase
import psycopg2

connection = None
fb = None


def reset_db_connection():
    global connection
    global fb
    connection = None
    fb = None


def get_db_connection():
    global connection
    global fb
    if not connection:
        connection = psycopg2.connect(
            dbname='fhirbase', user='postgres',
            host='fhirbase', port='5432')
        fb = fhirbase.FHIRBase(connection)
    return fb
