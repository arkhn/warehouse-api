import db
from models import resources

from .resource import Resource

resources_models = {}


def init():
    global resources_models
    client = db.get_db_connection()[db.DB_NAME]
    resource_list = client.list_collection_names()
    print("List of supported resources:", resource_list)
    for r in resource_list:
        if hasattr(resources, r):
            # if a resource has a specific implementation, use it
            resources_models[r] = getattr(resources, r)
        else:
            # if a resource has no specific implementation, create
            # a generic class inheriting from Resource.
            resources_models[r] = type(r, (Resource,), {})
