import elasticsearch
import pymongo

import fhirstore

from fhir_api import settings

connection = None
connection_es = None
store = None


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
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            username=settings.DB_USER,
            password=settings.DB_PASSWORD,
        )
    return connection


def get_es_connection():

    global connection_es
    if not connection_es:
        connection_es = elasticsearch.Elasticsearch([settings.ES_URL])
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
        store = fhirstore.FHIRStore(connection, connection_es, settings.DB_NAME)
        if not store.initialized:
            store.bootstrap()
    return store
