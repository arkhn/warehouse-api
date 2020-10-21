import logging

from fhir_api import db, settings

from . import resources
from .base import BaseResource

logger = logging.getLogger(__name__)

resources_models = {}


def init():
    global resources_models
    client = db.get_db_connection()[settings.DB_NAME]
    resource_list = client.list_collection_names()
    logger.debug("List of supported resources: %s", resource_list)
    for r in resource_list:
        if hasattr(resources, r):
            # if a resource has a specific implementation, use it
            resources_models[r] = getattr(resources, r)
        else:
            # if a resource has no specific implementation, create
            # a generic class inheriting from Resource.
            resources_models[r] = type(r, (BaseResource,), {})
