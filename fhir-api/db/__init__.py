import os
import pymongo
import fhirstore
import elasticsearch

connection = None
connection_es = None
store = None

DB_NAME = os.getenv("DB_NAME", "fhirstore")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "27017")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

ES_URL = os.getenv("ES_URL", "http://localhost:9200")


def reset_db_connection():
    global connection
    global connection_es
    global store
    connection = None
    connection_es = None
    store = None


def get_db_connection():
    global connection
    if not connection:
        connection = pymongo.MongoClient(
            host=DB_HOST, port=int(DB_PORT), username=DB_USER, password=DB_PASSWORD
        )
    return connection


def get_es_connection():
    global connection_es
    if not connection_es:
        connection_es = elasticsearch.Elasticsearch([ES_URL])
    return connection_es


def get_store():
    """
    get_store initializes a new FHIRStore instance
    it caches the resources loaded from the database in order
    to run this operation only once (at application startup)
    """
    global store
    connection = get_db_connection()
    connection_es = get_es_connection()
    if not store:
        store = fhirstore.FHIRStore(connection, connection_es, DB_NAME)
        if not store.initialized:
            store.bootstrap()
    return store
