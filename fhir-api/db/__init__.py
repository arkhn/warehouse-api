import os
import pymongo
import fhirstore

connection = None
store = None
cached_resources = None

DB_NAME = os.getenv("DB_NAME", "fhirstore")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "27017")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def reset_db_connection():
    global connection
    global store
    connection = None
    store = None


def get_db_connection():
    global connection
    if not connection:
        connection = pymongo.MongoClient(
            host=DB_HOST,
            port=int(DB_PORT),
            username=DB_USER,
            password=DB_PASSWORD
        )
    return connection

# get_store initializes a new FHIRStore instance
# it caches the resources loaded from the database in order
# to run this operation only once (at application startup)


def get_store():
    """
    get_store initializes a new FHIRStore instance
    it caches the resources loaded from the database in order
    to run this operation only once (at application startup)
    """
    global store
    global cached_resources
    connection = get_db_connection()
    if not store:
        store = fhirstore.FHIRStore(connection, DB_NAME)
        if not cached_resources:
            store.resume()
            cached_resources = store.resources
        else:
            store.resources = cached_resources
    return store
